from processors.data_processor import DataProcessor
from enrichment.google_places import GooglePlacesEnricher

# Mock data
raw_data = [
    {"email": "test@example.com", "phone": "1234567890", "company": "Test Corp"},
    {"email": "test2@example.com", "phone": "0987654321", "company": "Another Co"}
]

print("--- Testing Enricher Directly ---")
enricher = GooglePlacesEnricher()
enriched_lead = enricher.enrich(raw_data[0].copy())
print(f"Original: {raw_data[0]}")
print(f"Enriched: {enriched_lead}")

print("\n--- Testing DataProcessor Integration ---")
processor = DataProcessor(raw_data)
cleaned_df = processor.clean_data()
print("Processed DataFrame columns:", cleaned_df.columns.tolist())
print("First row enriched data:", cleaned_df.iloc[0].to_dict())

if 'rating' in cleaned_df.columns and 'enrichment_source' in cleaned_df.columns:
    print("\nSUCCESS: Enrichment fields found in processed data.")
else:
    print("\nFAILURE: Enrichment fields missing.")
