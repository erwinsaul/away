#!/bin/bash
# Script de backup para el Sistema de Gestión de Laboratorios
# Uso: ./backup.sh

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Sistema de Backup - Away Laboratorios ===${NC}"
echo ""

# Crear directorio de backups si no existe
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Crear backup sin comprimir
echo "📋 Creando copia de seguridad de la base de datos..."
cp data/laboratorios.db "$BACKUP_DIR/laboratorios_backup_${TIMESTAMP}.db"

# Crear backup comprimido
echo "🗜️  Creando archivo comprimido..."
tar -czf "$BACKUP_DIR/backup_completo_${TIMESTAMP}.tar.gz" data/laboratorios.db

# Verificar integridad
echo "✓ Verificando integridad..."
MATERIAS=$(sqlite3 "$BACKUP_DIR/laboratorios_backup_${TIMESTAMP}.db" "SELECT COUNT(*) FROM materias")
ESTUDIANTES=$(sqlite3 "$BACKUP_DIR/laboratorios_backup_${TIMESTAMP}.db" "SELECT COUNT(*) FROM estudiantes")
CALIFICACIONES=$(sqlite3 "$BACKUP_DIR/laboratorios_backup_${TIMESTAMP}.db" "SELECT COUNT(*) FROM calificaciones")

echo ""
echo -e "${GREEN}✓ Backup completado exitosamente!${NC}"
echo ""
echo "📊 Contenido respaldado:"
echo "   - Materias: $MATERIAS"
echo "   - Estudiantes: $ESTUDIANTES"
echo "   - Calificaciones: $CALIFICACIONES"
echo ""
echo "📁 Archivos creados:"
ls -lh "$BACKUP_DIR/laboratorios_backup_${TIMESTAMP}.db" "$BACKUP_DIR/backup_completo_${TIMESTAMP}.tar.gz"
echo ""
echo "💾 Ubicación: $(pwd)/$BACKUP_DIR/"
echo ""

# Limpiar backups antiguos (mantener solo los últimos 10)
echo "🧹 Limpiando backups antiguos (manteniendo los últimos 10)..."
cd "$BACKUP_DIR"
ls -t laboratorios_backup_*.db 2>/dev/null | tail -n +11 | xargs -r rm
ls -t backup_completo_*.tar.gz 2>/dev/null | tail -n +11 | xargs -r rm
cd ..

echo -e "${GREEN}✓ Proceso completado${NC}"
