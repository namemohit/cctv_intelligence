"""
Detection Analysis and Query Utility

Analyze, query, and visualize detection logs from the database
"""

import sqlite3
import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import argparse


class DetectionAnalyzer:
    """Analyze detection logs from database and files."""

    def __init__(self, db_path: str = None, log_dir: str = "detections_log"):
        """
        Initialize analyzer.

        Args:
            db_path: Path to database file
            log_dir: Log directory (auto-find latest DB if db_path not provided)
        """
        self.log_dir = Path(log_dir)

        if db_path:
            self.db_path = db_path
        else:
            # Find latest database
            db_files = list(self.log_dir.glob("detections_*.db"))
            if not db_files:
                raise FileNotFoundError(f"No database found in {log_dir}")
            self.db_path = max(db_files, key=lambda p: p.stat().st_mtime)

        print(f"Using database: {self.db_path}")

    def get_summary_stats(self) -> Dict:
        """Get overall summary statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total detections
        cursor.execute('SELECT COUNT(*) FROM detections')
        total = cursor.fetchone()[0]

        # Time range
        cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM detections')
        min_time, max_time = cursor.fetchone()

        # Classes detected
        cursor.execute('SELECT COUNT(DISTINCT class_name) FROM detections')
        unique_classes = cursor.fetchone()[0]

        # Cameras
        cursor.execute('SELECT COUNT(DISTINCT source) FROM detections')
        cameras = cursor.fetchone()[0]

        conn.close()

        return {
            'total_detections': total,
            'start_time': min_time,
            'end_time': max_time,
            'unique_classes': unique_classes,
            'cameras': cameras
        }

    def get_detections_by_class(self) -> List[Tuple]:
        """Get detection count by class."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT class_name, COUNT(*) as count
            FROM detections
            GROUP BY class_name
            ORDER BY count DESC
        ''')

        results = cursor.fetchall()
        conn.close()

        return results

    def get_detections_by_source(self) -> List[Tuple]:
        """Get detection count by source/camera."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT source, COUNT(*) as count
            FROM detections
            GROUP BY source
            ORDER BY count DESC
        ''')

        results = cursor.fetchall()
        conn.close()

        return results

    def get_detections_by_time(self, interval: str = "hour") -> List[Tuple]:
        """
        Get detections grouped by time.

        Args:
            interval: 'hour', 'day', or 'minute'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if interval == "hour":
            group_format = "%Y-%m-%d %H:00"
        elif interval == "day":
            group_format = "%Y-%m-%d"
        elif interval == "minute":
            group_format = "%Y-%m-%d %H:%M"
        else:
            raise ValueError(f"Invalid interval: {interval}")

        cursor.execute(f'''
            SELECT strftime('{group_format}', timestamp) as time_period,
                   COUNT(*) as count
            FROM detections
            GROUP BY time_period
            ORDER BY time_period
        ''')

        results = cursor.fetchall()
        conn.close()

        return results

    def get_high_confidence_detections(self, min_confidence: float = 0.9) -> List[Dict]:
        """Get detections above confidence threshold."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp, source, class_name, confidence
            FROM detections
            WHERE confidence >= ?
            ORDER BY confidence DESC
        ''', (min_confidence,))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[0],
                'source': row[1],
                'class': row[2],
                'confidence': row[3]
            }
            for row in results
        ]

    def get_detections_by_time_range(self, start: str, end: str) -> List[Dict]:
        """
        Get detections in time range.

        Args:
            start: ISO format datetime (e.g., "2024-03-13T10:00:00")
            end: ISO format datetime
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp, source, class_name, confidence, frame_number
            FROM detections
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp
        ''', (start, end))

        results = cursor.fetchall()
        conn.close()

        return [
            {
                'timestamp': row[0],
                'source': row[1],
                'class': row[2],
                'confidence': row[3],
                'frame': row[4]
            }
            for row in results
        ]

    def get_class_distribution(self, class_name: str) -> List[Tuple]:
        """Get detections distribution for specific class."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT source, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM detections
            WHERE class_name = ?
            GROUP BY source
            ORDER BY count DESC
        ''', (class_name,))

        results = cursor.fetchall()
        conn.close()

        return results

    def export_to_csv(self, output_file: str, query: str = None):
        """Export detections to CSV file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if query:
            cursor.execute(query)
        else:
            cursor.execute('SELECT * FROM detections')

        # Get column names
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Write CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        conn.close()
        print(f"Exported {len(rows)} rows to {output_file}")

    def get_statistics_report(self) -> str:
        """Generate detailed statistics report."""
        stats = self.get_summary_stats()
        by_class = self.get_detections_by_class()
        by_source = self.get_detections_by_source()
        by_hour = self.get_detections_by_time('hour')

        report = f"""
{'='*60}
DETECTION STATISTICS REPORT
{'='*60}

OVERALL SUMMARY
{'-'*60}
Total Detections: {stats['total_detections']}
Time Range: {stats['start_time']} to {stats['end_time']}
Unique Classes: {stats['unique_classes']}
Cameras: {stats['cameras']}

DETECTIONS BY CLASS
{'-'*60}
"""
        for class_name, count in by_class:
            report += f"{class_name:20} {count:10}\n"

        report += f"\nDETECTIONS BY CAMERA\n{'-'*60}\n"
        for source, count in by_source:
            report += f"{source:20} {count:10}\n"

        report += f"\nDETECTIONS BY HOUR (Recent)\n{'-'*60}\n"
        for time_period, count in by_hour[-24:]:  # Last 24 hours
            report += f"{time_period:20} {count:10}\n"

        report += f"\n{'='*60}\n"

        return report

    def print_report(self):
        """Print detailed report to console."""
        print(self.get_statistics_report())

    def save_report(self, filename: str):
        """Save report to file."""
        with open(filename, 'w') as f:
            f.write(self.get_statistics_report())
        print(f"Report saved to {filename}")


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description='Analyze detection logs')

    parser.add_argument('--db', help='Database file path')
    parser.add_argument('--log-dir', default='detections_log',
                       help='Log directory')

    subparsers = parser.add_subparsers(dest='command')

    # Summary command
    subparsers.add_parser('summary', help='Show summary statistics')

    # Classes command
    subparsers.add_parser('classes', help='Show detections by class')

    # Sources command
    subparsers.add_parser('sources', help='Show detections by camera')

    # Time command
    time_parser = subparsers.add_parser('time', help='Show detections over time')
    time_parser.add_argument('--interval', choices=['hour', 'day', 'minute'],
                           default='hour')

    # High confidence command
    conf_parser = subparsers.add_parser('high-conf',
                                       help='Show high confidence detections')
    conf_parser.add_argument('--min', type=float, default=0.9,
                           help='Minimum confidence')

    # Range command
    range_parser = subparsers.add_parser('range',
                                        help='Get detections in time range')
    range_parser.add_argument('--start', required=True,
                            help='Start time (ISO format)')
    range_parser.add_argument('--end', required=True,
                            help='End time (ISO format)')

    # Class distribution command
    dist_parser = subparsers.add_parser('dist',
                                       help='Get class distribution')
    dist_parser.add_argument('--class', dest='class_name', required=True,
                           help='Class name')

    # Export command
    export_parser = subparsers.add_parser('export',
                                         help='Export to CSV')
    export_parser.add_argument('--output', required=True,
                             help='Output CSV file')

    # Report command
    report_parser = subparsers.add_parser('report',
                                         help='Generate full report')
    report_parser.add_argument('--output', help='Save report to file')

    args = parser.parse_args()

    try:
        analyzer = DetectionAnalyzer(args.db, args.log_dir)

        if args.command == 'summary':
            stats = analyzer.get_summary_stats()
            print("\n" + "="*60)
            print("SUMMARY STATISTICS")
            print("="*60)
            for key, value in stats.items():
                print(f"{key:20} {value}")
            print("="*60 + "\n")

        elif args.command == 'classes':
            print("\n" + "="*60)
            print("DETECTIONS BY CLASS")
            print("="*60)
            for class_name, count in analyzer.get_detections_by_class():
                print(f"{class_name:20} {count:10}")
            print("="*60 + "\n")

        elif args.command == 'sources':
            print("\n" + "="*60)
            print("DETECTIONS BY CAMERA")
            print("="*60)
            for source, count in analyzer.get_detections_by_source():
                print(f"{source:20} {count:10}")
            print("="*60 + "\n")

        elif args.command == 'time':
            print("\n" + "="*60)
            print(f"DETECTIONS BY {args.interval.upper()}")
            print("="*60)
            for time_period, count in analyzer.get_detections_by_time(args.interval):
                print(f"{time_period:20} {count:10}")
            print("="*60 + "\n")

        elif args.command == 'high-conf':
            print(f"\n Detections with confidence >= {args.min}\n")
            for det in analyzer.get_high_confidence_detections(args.min):
                print(f"{det['timestamp']} | {det['source']:15} | "
                      f"{det['class']:15} | {det['confidence']:.2f}")

        elif args.command == 'range':
            print(f"\nDetections from {args.start} to {args.end}\n")
            for det in analyzer.get_detections_by_time_range(args.start, args.end):
                print(f"{det['timestamp']} | {det['source']:15} | "
                      f"{det['class']:15} | {det['confidence']:.2f}")

        elif args.command == 'dist':
            print(f"\n{args.class_name} Distribution by Camera\n")
            for source, count, avg_conf in analyzer.get_class_distribution(args.class_name):
                print(f"{source:20} Count: {count:5} Avg Conf: {avg_conf:.2f}")

        elif args.command == 'export':
            analyzer.export_to_csv(args.output)

        elif args.command == 'report':
            if args.output:
                analyzer.save_report(args.output)
            else:
                analyzer.print_report()

        else:
            # Default: print full report
            analyzer.print_report()

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
