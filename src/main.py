from collectors.real_estate_collector import RealEstateCollector
from collectors.tutor_collector import TutorCollector
from collectors.service_provider_collector import ServiceProviderCollector
from processors.data_processor import DataProcessor
from generators.report_generator import ReportGenerator
import os
from database import init_db, SessionLocal
from logger import logger

def run_niche(collector_class, niche_name, db_session):
    logger.info(f"--- Processing {niche_name} ---")
    
    # 1. Collection
    collector = collector_class(db_session)
    collector.collect(num_samples=20)
    raw_data = collector.data
    
    if not raw_data:
        logger.warning(f"No data collected for {niche_name}.")
        return

    # 2. Processing
    processor = DataProcessor(raw_data)
    cleaned_df = processor.clean_data()
    scored_df = processor.score_leads()
    
    logger.info(f"Processed {len(scored_df)} leads.")
    
    # 3. Reporting
    generator = ReportGenerator()
    generator.generate_pdf(scored_df, title=f"{niche_name} Leads")
    generator.generate_excel(scored_df, filename=f"{niche_name.lower().replace(' ', '_')}_leads.xlsx")

def main():
    logger.info("Starting LeadForge System...")
    
    # Initialize Database
    init_db()
    db = SessionLocal()
    
    niches = [
        (RealEstateCollector, "Real Estate"),
        (TutorCollector, "Tutors"),
        (ServiceProviderCollector, "Service Providers")
    ]
    
    try:
        for collector_cls, name in niches:
            try:
                run_niche(collector_cls, name, db)
            except Exception as e:
                logger.error(f"Error processing {name}: {e}")
    finally:
        db.close()
    
    logger.info("All niches processed.")

if __name__ == "__main__":
    main()
