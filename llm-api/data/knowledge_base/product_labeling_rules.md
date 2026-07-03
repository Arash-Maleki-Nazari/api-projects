# Product Labeling Knowledge Base

This API classifies e-commerce products using price, inventory, and description quality.

Price rules:
- Products below 50 are budget products.
- Products from 50 to 200 are mid-range products.
- Products above 200 are premium products.

Inventory rules:
- Inventory above 1000 is high-stock.
- Inventory below 10 is low-stock and should trigger reorder.

Description rules:
- Long descriptions with more than 500 characters are considered detailed descriptions.

LLM enrichment can add subcategory, quality assessment, marketing angle, and customer segment.
