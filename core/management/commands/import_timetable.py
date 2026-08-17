import os
from django.core.management.base import BaseCommand
from core.services.timetable.importer import import_timetable
from core.services.timetable.json_importer import import_timetable_json


class Command(BaseCommand):
    help = 'Imports an Excel workbook (.xlsx) or JSON file into the CSE SmartRoom Django/PostgreSQL database.'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel (.xlsx) or JSON (.json) timetable file.')
        parser.add_argument('--academic-year', type=str, default='2026-27', help='Academic session year (default: 2026-27).')

    def handle(self, *args, **options):
        file_path = options['file_path']
        academic_year = options['academic_year']

        self.stdout.write("CSE SmartRoom Timetable Import")
        self.stdout.write("--------------------------------")

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        file_name = os.path.basename(file_path)

        # Determine importer based on file extension
        if file_path.lower().endswith('.json'):
            result = import_timetable_json(file_path, academic_year=academic_year)
        else:
            result = import_timetable(file_path, academic_year=academic_year)

        if result.success:
            self.stdout.write(f"File: {file_name}")
            self.stdout.write(f"Semester: {result.semester}")
            self.stdout.write("")
            self.stdout.write(f"Sections: {result.sections_count}")
            self.stdout.write(f"Entries parsed: {result.parsed_count}")
            self.stdout.write(f"Entries imported: {result.imported_count}")
            self.stdout.write(f"Merge groups: {result.merge_groups_count}")
            self.stdout.write(f"Laboratories: {result.laboratories_count}")
            self.stdout.write(f"Free periods: {result.free_periods_count}")
            self.stdout.write(f"Warnings: {result.warning_count}")
            self.stdout.write(f"Errors: {result.error_count}")
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("IMPORT SUCCESSFUL"))
        else:
            self.stdout.write(self.style.ERROR("IMPORT FAILED"))
            self.stdout.write("")
            self.stdout.write(f"Errors: {result.error_count}")
            self.stdout.write("")

            for err in result.errors:
                err_code = err.get('error_code', 'ERROR')
                self.stdout.write(f"[{err_code}]")
                if err.get('sheet'):
                    self.stdout.write(f"Sheet: {err['sheet']}")
                if err.get('cell'):
                    self.stdout.write(f"Cell: {err['cell']}")
                if err.get('section'):
                    self.stdout.write(f"Section: {err['section']}")
                if err.get('day'):
                    self.stdout.write(f"Day: {err['day']}")
                if err.get('period'):
                    self.stdout.write(f"Period: {err['period']}")
                self.stdout.write(f"Message: {err.get('message', '')}")
                self.stdout.write("")

            self.stdout.write("Database changes rolled back.")
