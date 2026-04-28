# Backups - Sistema de Gestión de Laboratorios

Este directorio contiene las copias de seguridad de la base de datos del sistema.

## 📋 Tipos de Backup

1. **Backup sin comprimir** (`laboratorios_backup_YYYYMMDD_HHMMSS.db`)
   - Base de datos SQLite completa
   - Listo para usar inmediatamente
   - Tamaño: ~100KB

2. **Backup comprimido** (`backup_completo_YYYYMMDD_HHMMSS.tar.gz`)
   - Archivo comprimido tar.gz
   - Ahorra espacio (~16KB)
   - Requiere descompresión antes de usar

## 🔧 Cómo Crear un Backup

### Opción 1: Script automatizado (Recomendado)
```bash
./backup.sh
```

### Opción 2: Manual
```bash
# Backup simple
cp data/laboratorios.db backups/laboratorios_backup_$(date +%Y%m%d_%H%M%S).db

# Backup comprimido
tar -czf backups/backup_completo_$(date +%Y%m%d_%H%M%S).tar.gz data/laboratorios.db
```

## 🔄 Cómo Restaurar un Backup

### Desde backup sin comprimir:
```bash
# 1. Detener la aplicación
# 2. Hacer backup del archivo actual (por seguridad)
cp data/laboratorios.db data/laboratorios_old.db

# 3. Restaurar el backup
cp backups/laboratorios_backup_YYYYMMDD_HHMMSS.db data/laboratorios.db

# 4. Reiniciar la aplicación
```

### Desde backup comprimido:
```bash
# 1. Detener la aplicación
# 2. Descomprimir
tar -xzf backups/backup_completo_YYYYMMDD_HHMMSS.tar.gz

# 3. El archivo se extrae en data/laboratorios.db automáticamente
# 4. Reiniciar la aplicación
```

## 📊 Verificar Integridad de un Backup

```bash
sqlite3 backups/laboratorios_backup_YYYYMMDD_HHMMSS.db "
SELECT 'Materias: ' || COUNT(*) FROM materias
UNION ALL SELECT 'Paralelos: ' || COUNT(*) FROM paralelos
UNION ALL SELECT 'Estudiantes: ' || COUNT(*) FROM estudiantes
UNION ALL SELECT 'Laboratorios: ' || COUNT(*) FROM laboratorios
UNION ALL SELECT 'Calificaciones: ' || COUNT(*) FROM calificaciones;
"
```

## 🧹 Gestión de Backups

El script `backup.sh` automáticamente:
- ✅ Mantiene los últimos 10 backups
- ✅ Elimina backups antiguos automáticamente
- ✅ Verifica la integridad de cada backup

## ⚠️ Recomendaciones

1. **Realizar backups regularmente** - Antes de cambios importantes
2. **Mantener backups en ubicaciones diferentes** - Copiar a otro disco/servidor
3. **Verificar la integridad** - Probar restauraciones periódicamente
4. **Documentar restauraciones** - Anotar qué backup se restauró y cuándo

## 📅 Último Backup

- **Fecha:** 2025-11-20 17:59
- **Materias:** 5
- **Paralelos:** 12
- **Estudiantes:** 115
- **Laboratorios:** 60
- **Calificaciones:** 632
- **Tamaño:** 172KB (sin comprimir), 36KB (comprimido)

## 📈 Historial de Crecimiento

| Fecha | Estudiantes | Calificaciones | Tamaño |
|-------|-------------|----------------|--------|
| 19/11 18:19 | 39 | 268 | 100KB |
| 20/11 12:06 | 104 | 547 | 160KB |
| 20/11 17:59 | 115 | 632 | 172KB |

---
*Sistema de Gestión de Laboratorios - Away*
*Desarrollado por: ErwinSaul*
