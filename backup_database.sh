#!/bin/bash
# Automated backup script for Village Health Tracking System
# This script creates backups of the database and uploaded photos

# Configuration
DB_FILE="health_tracking.db"
BACKUP_DIR="backups"
PHOTOS_DIR="uploaded_photos"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Village Health Tracking System - Backup"
echo "=========================================="
echo ""

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${YELLOW}Creating backup directory...${NC}"
    mkdir -p "$BACKUP_DIR"
fi

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "ERROR: Database file '$DB_FILE' not found!"
    exit 1
fi

# Backup database file
echo -e "${GREEN}1. Backing up database...${NC}"
cp "$DB_FILE" "$BACKUP_DIR/health_tracking_$DATE.db"
if [ $? -eq 0 ]; then
    echo "   ✓ Database backup created: health_tracking_$DATE.db"
else
    echo "   ✗ Database backup failed!"
    exit 1
fi

# Backup photos directory if it exists
if [ -d "$PHOTOS_DIR" ]; then
    echo -e "${GREEN}2. Backing up photos...${NC}"
    tar -czf "$BACKUP_DIR/photos_$DATE.tar.gz" "$PHOTOS_DIR" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "   ✓ Photos backup created: photos_$DATE.tar.gz"
    else
        echo "   ✗ Photos backup failed!"
    fi
else
    echo -e "${YELLOW}2. No photos directory found, skipping...${NC}"
fi

# Create SQL dump (for portability)
echo -e "${GREEN}3. Creating SQL dump...${NC}"
if command -v sqlite3 &> /dev/null; then
    sqlite3 "$DB_FILE" .dump | gzip > "$BACKUP_DIR/health_tracking_$DATE.sql.gz"
    if [ $? -eq 0 ]; then
        echo "   ✓ SQL dump created: health_tracking_$DATE.sql.gz"
    else
        echo "   ✗ SQL dump failed!"
    fi
else
    echo "   ℹ sqlite3 command not found, skipping SQL dump"
fi

# Remove old backups (older than retention period)
echo -e "${GREEN}4. Cleaning old backups (older than $RETENTION_DAYS days)...${NC}"
find "$BACKUP_DIR" -name "health_tracking_*.db" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$BACKUP_DIR" -name "photos_*.tar.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
find "$BACKUP_DIR" -name "health_tracking_*.sql.gz" -mtime +$RETENTION_DAYS -delete 2>/dev/null
echo "   ✓ Old backups cleaned"

# Display backup summary
echo ""
echo "=========================================="
echo "Backup Summary"
echo "=========================================="
echo "Backup completed: $DATE"
echo "Location: $BACKUP_DIR/"
echo ""
echo "Recent backups:"
ls -lh "$BACKUP_DIR" | tail -5

# Calculate total backup size
BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
echo ""
echo "Total backup size: $BACKUP_SIZE"
echo "=========================================="
echo -e "${GREEN}Backup completed successfully!${NC}"
