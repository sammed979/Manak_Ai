from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.product import Product, ProductStandardMatch, ProductCategory
from app.models.standard import Standard
from app.ai.embeddings import EmbeddingService, cosine_similarity
import json


class ProductStandardMatcher:
    def __init__(self, embedding_service: EmbeddingService, db: Session):
        self.embedding_service = embedding_service
        self.db = db
    
    async def match_product_to_standards(
        self,
        product: Product,
        top_k: int = 10
    ) -> List[ProductStandardMatch]:
        """
        Match a product to applicable standards using multiple strategies
        """
        matches = []
        
        # Get all standards
        standards = self.db.query(Standard).all()
        
        # Strategy 1: Category-based matching
        category_matches = self._match_by_category(product, standards)
        matches.extend(category_matches)
        
        # Strategy 2: Keyword-based matching
        keyword_matches = await self._match_by_keywords(product, standards)
        matches.extend(keyword_matches)
        
        # Strategy 3: Description-based similarity
        similarity_matches = await self._match_by_similarity(product, standards)
        matches.extend(similarity_matches)
        
        # Deduplicate and score
        deduped_matches = self._deduplicate_matches(matches)
        
        # Sort by score and return top_k
        deduped_matches.sort(key=lambda x: x.match_score or 0, reverse=True)
        return deduped_matches[:top_k]
    
    def _match_by_category(
        self,
        product: Product,
        standards: List[Standard]
    ) -> List[ProductStandardMatch]:
        """
        Match based on product category and standard category/subcategory
        """
        matches = []
        
        category_keywords = {
            ProductCategory.ELECTRICAL: ["electrical", "appliance", "voltage", "current", "power"],
            ProductCategory.FOOD: ["food", "beverage", "consumable", "edible"],
            ProductCategory.TEXTILES: ["textile", "fabric", "clothing", "garment"],
            ProductCategory.METALS: ["metal", "steel", "iron", "aluminum", "copper"],
            ProductCategory.PLASTICS: ["plastic", "polymer", "pvc", "pe"],
            ProductCategory.CONSTRUCTION: ["construction", "building", "cement", "concrete"],
            ProductCategory.AUTOMOTIVE: ["automotive", "vehicle", "car", "motor"],
            ProductCategory.CHEMICALS: ["chemical", "compound", "substance"],
            ProductCategory.PRECIOUS_METALS: ["gold", "silver", "jewelry", "hallmark"]
        }
        
        keywords = category_keywords.get(product.category, [])
        
        for standard in standards:
            score = 0.0
            reasons = []
            
            # Check title and scope
            text_to_check = f"{standard.title} {standard.category or ''} {standard.subcategory or ''}".lower()
            
            for keyword in keywords:
                if keyword in text_to_check:
                    score += 0.3
                    reasons.append(f"Category keyword '{keyword}' found")
            
            if score > 0:
                match = ProductStandardMatch(
                    product_id=product.id,
                    standard_id=standard.id,
                    match_score=min(score, 1.0),
                    match_reason="; ".join(reasons),
                    is_mandatory="UNKNOWN"
                )
                matches.append(match)
        
        return matches
    
    async def _match_by_keywords(
        self,
        product: Product,
        standards: List[Standard]
    ) -> List[ProductStandardMatch]:
        """
        Match based on product description keywords
        """
        matches = []
        
        if not product.description:
            return matches
        
        # Extract keywords from product description
        description_lower = product.description.lower()
        
        for standard in standards:
            # Check if standard title or category appears in description
            standard_text = f"{standard.title} {standard.category or ''} {standard.subcategory or ''}".lower()
            
            # Simple word overlap
            description_words = set(description_lower.split())
            standard_words = set(standard_text.split())
            
            overlap = description_words.intersection(standard_words)
            
            if len(overlap) > 0:
                score = min(len(overlap) / len(standard_words), 1.0)
                match = ProductStandardMatch(
                    product_id=product.id,
                    standard_id=standard.id,
                    match_score=score,
                    match_reason=f"Keyword overlap: {', '.join(list(overlap)[:5])}",
                    is_mandatory="UNKNOWN"
                )
                matches.append(match)
        
        return matches
    
    async def _match_by_similarity(
        self,
        product: Product,
        standards: List[Standard]
    ) -> List[ProductStandardMatch]:
        """
        Match using semantic similarity between product description and standard title
        """
        matches = []
        
        if not product.description:
            return matches
        
        # Get embedding for product description
        product_embedding = await self.embedding_service.embed_text(product.description)
        
        for standard in standards:
            # Get embedding for standard title
            standard_embedding = await self.embedding_service.embed_text(standard.title)
            
            # Calculate similarity
            similarity = cosine_similarity(product_embedding, standard_embedding)
            
            if similarity > 0.3:  # Threshold for similarity
                match = ProductStandardMatch(
                    product_id=product.id,
                    standard_id=standard.id,
                    match_score=similarity,
                    match_reason=f"Semantic similarity: {similarity:.2f}",
                    is_mandatory="UNKNOWN"
                )
                matches.append(match)
        
        return matches
    
    def _deduplicate_matches(
        self,
        matches: List[ProductStandardMatch]
    ) -> List[ProductStandardMatch]:
        """
        Deduplicate matches by standard_id, keeping the highest score
        """
        match_dict = {}
        
        for match in matches:
            key = str(match.standard_id)
            if key not in match_dict:
                match_dict[key] = match
            else:
                # Keep the match with higher score
                if (match.match_score or 0) > (match_dict[key].match_score or 0):
                    match_dict[key] = match
        
        return list(match_dict.values())
    
    def save_matches(self, matches: List[ProductStandardMatch]):
        """
        Save matches to database
        """
        for match in matches:
            self.db.add(match)
        self.db.commit()
