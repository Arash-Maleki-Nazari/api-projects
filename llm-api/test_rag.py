from src.services.rag_service import LocalRAGService

rag = LocalRAGService()

indexed_count = rag.index_documents()
print(f"Indexed documents: {indexed_count}")

results = rag.search("What makes a product premium?", top_k=3)

print("\nSearch results:")
for index, result in enumerate(results, start=1):
    print(f"\nResult {index}")
    print(f"Distance: {result['distance']}")
    print(f"Source: {result['metadata']['source']}")
    print(result["text"])
