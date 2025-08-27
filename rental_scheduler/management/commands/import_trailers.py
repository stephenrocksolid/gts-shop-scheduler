from django.core.management.base import BaseCommand
from rental_scheduler.models import Trailer, TrailerCategory
import csv
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import trailers from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        success_count = 0
        error_count = 0
        
        logger.info(f"Starting trailer import from {csv_file}")
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.DictReader(file)
                total_rows = sum(1 for row in reader)
                logger.info(f"Found {total_rows} trailers to import")
                
                # Reset file pointer
                file.seek(0)
                next(reader)  # Skip header row
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Log the row being processed
                        logger.info(f"Processing row {row_num}: {row['number']} - {row['model']}")
                        
                        # Get or create the category
                        category, created = TrailerCategory.objects.get_or_create(
                            category=row['category']
                        )
                        if created:
                            logger.info(f"Created new category: {category.category}")
                        
                        # Create the trailer
                        size_str = row['size']
                        width_val = None
                        length_val = None
                        if size_str:
                            parts = size_str.replace("'", '').replace('"', '').lower().strip().split('x')
                            if len(parts) == 2:
                                try:
                                    width_val = Decimal(parts[0].strip())
                                    length_val = Decimal(parts[1].strip())
                                except Exception:
                                    pass
                        trailer = Trailer.objects.create(
                            category=category,
                            number=row['number'],
                            width=width_val,
                            length=length_val,
                            model=row['model'],
                            hauling_capacity=Decimal(row['hauling_capacity']),
                            half_day_rate=Decimal(row['half_day_rate']),
                            daily_rate=Decimal(row['daily_rate']),
                            weekly_rate=Decimal(row['weekly_rate']),
                            is_available=row['is_available'].lower() == 'true'
                        )
                        
                        success_count += 1
                        logger.info(f"Successfully imported trailer: {trailer.number}")
                        
                    except Exception as e:
                        error_count += 1
                        logger.error(f"Error importing row {row_num}: {str(e)}")
                        logger.error(f"Row data: {row}")
                        continue
                
                logger.info(f"Import completed. Success: {success_count}, Errors: {error_count}")
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported {success_count} trailers. {error_count} errors encountered.'
                ))
                
        except Exception as e:
            logger.error(f"Fatal error during import: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}')) 