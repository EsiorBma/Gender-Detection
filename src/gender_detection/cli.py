"""Command-line interface for gender detection."""

import argparse
import sys
from pathlib import Path

from .model import GenderClassifier
from .database import db


def predict_command(args):
    """Handle predict command."""
    classifier = GenderClassifier()
    
    if args.batch:
        # Batch prediction from file
        with open(args.batch, 'r', encoding='utf-8') as f:
            names = [line.strip() for line in f if line.strip()]
        
        print(f"Processing {len(names)} names...\n")
        
        for name in names:
            result = classifier.predict(name)
            print(f"{name:<40} -> {result['gender']}")
    else:
        # Single prediction
        result = classifier.predict(args.name)
        
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\nNom complet: {args.name}")
            print(f"Nom de famille: {result['surname']}")
            print(f"Prénom(s): {', '.join(result['first_names'])}")
            print(f"Prénom principal: {result['main_first_name']}")
            print(f"Genre prédit: {result['gender']}")


def train_command(args):
    """Handle train command."""
    from .model import train_model
    
    print("Training model...")
    train_model()
    print("✓ Model trained successfully!")


def update_command(args):
    """Handle update command."""
    from .model import update_model_with_feedback
    
    print("Updating model with feedback...")
    update_model_with_feedback()
    print("✓ Model updated successfully!")


def stats_command(args):
    """Handle stats command."""
    stats = db.get_feedback_stats()
    
    print("\n📊 Feedback Statistics")
    print("=" * 50)
    print(f"Total predictions: {stats['total']}")
    print(f"With feedback: {stats['with_feedback']}")
    print(f"Accuracy: {stats['accuracy']}%")
    print(f"Last feedback: {stats['last_feedback']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Gender Detection CLI for Togolese Names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s predict "AMEGANVI Koffi Ama"
  %(prog)s predict "KOKOU Mensah" --json
  %(prog)s predict --batch names.txt
  %(prog)s train
  %(prog)s update
  %(prog)s stats
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict gender from name')
    predict_parser.add_argument('name', nargs='?', help='Full name to analyze')
    predict_parser.add_argument(
        '--batch', '-b',
        help='File with names (one per line) for batch prediction'
    )
    predict_parser.add_argument(
        '--json', '-j',
        action='store_true',
        help='Output in JSON format'
    )
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train the model')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update model with feedback')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show feedback statistics')
    
    args = parser.parse_args()
    
    if args.command == 'predict':
        if not args.name and not args.batch:
            predict_parser.error("Either name or --batch is required")
        predict_command(args)
    elif args.command == 'train':
        train_command(args)
    elif args.command == 'update':
        update_command(args)
    elif args.command == 'stats':
        stats_command(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
