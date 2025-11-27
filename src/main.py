from collectors.real_estate_collector import RealEstateCollector
from collectors.tutor_collector import TutorCollector
from collectors.service_provider_collector import ServiceProviderCollector
from processors.data_processor import DataProcessor
from generators.report_generator import ReportGenerator
import os

def run_niche(collector_class, niche_name):
    print(f"\n--- Processing {niche_name} ---")
    
    # 1. Collection
    collector = collector_class()
    collector.collect(num_samples=20)
    raw_data = collector.data
    
    if not raw_data:
        print(f"No data collected for {niche_name}.")
        return

    # 2. Processing
    processor = DataProcessor(raw_data)
    cleaned_df = processor.clean_data()
    scored_df = processor.score_leads()
    
    print(f"Processed {len(scored_df)} leads.")
    
    # 3. Reporting
    generator = ReportGenerator()
    generator.generate_pdf(scored_df, title=f"{niche_name} Leads")
    generator.generate_excel(scored_df, filename=f"{niche_name.lower().replace(' ', '_')}_leads.xlsx")

def main():
    print("Starting Lead Generation System...")
    
    niches = [
        (RealEstateCollector, "Real Estate"),
        (TutorCollector, "Tutors"),
        (ServiceProviderCollector, "Service Providers")
    ]
    
    for collector_cls, name in niches:
        try:
            run_niche(collector_cls, name)
        except Exception as e:
            print(f"Error processing {name}: {e}")
    
    print("\nAll niches processed.")

if __name__ == "__main__":
    main()
