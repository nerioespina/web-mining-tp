Select publicacion, count(1) From inmuebles group by 1 order by 2 desc;
Hoy             | 2303
Ayer            | 728
Hace 2 días     | 247
07/04/2025      | 233
Hace 5 días     | 176
Hace 3 días     | 136
09/04/2025      | 135
08/04/2025      | 132
Hace 4 días     | 126
31/03/2025      | 100
06/04/2025      | 89
11/03/2025      | 68
01/04/2025      | 67
03/04/2025      | 64
26/03/2025      | 44
17/03/2025      | 42
27/03/2025      | 40
18/03/2025      | 38
28/03/2025      | 37
21/03/2025      | 36
10/03/2025      | 35
19/03/2025      | 34
13/03/2025      | 33
05/04/2025      | 33
02/04/2025      | 32
...

Descartamos la fecha de publicacion

---------------
CREATE TABLE categoria (
	"id"	INTEGER NOT NULL,
	"descripcion"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);

INSERT INTO categoria(descripcion) Select distinct categoria from inmuebles;
ALTER TABLE inmuebles ADD COLUMN categoria_id INTEGER;
UPDATE inmuebles SET categoria_id = (Select id from categoria where descripcion = inmuebles.categoria);
ALTER TABLE inmuebles DROP COLUMN categoria;

---------------
UPDATE inmuebles SET antiguedad = 'Sin información' where antiguedad is null;
CREATE TABLE antiguedad (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO antiguedad(descripcion) Select distinct antiguedad from inmuebles;
ALTER TABLE inmuebles ADD COLUMN antiguedad_id INTEGER;
UPDATE inmuebles SET antiguedad_id = (Select id from antiguedad where descripcion = inmuebles.antiguedad);
ALTER TABLE inmuebles DROP COLUMN antiguedad;

---------------
UPDATE inmuebles SET banos = 'Sin información' where banos is null;
CREATE TABLE banos (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO banos(descripcion) Select distinct banos from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN banos_id INTEGER;
UPDATE inmuebles SET banos_id = (Select id from banos where descripcion = inmuebles.banos);
ALTER TABLE inmuebles DROP COLUMN banos;

---------------
UPDATE inmuebles SET ambientes = 'Sin información' where ambientes is null;
CREATE TABLE ambientes (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO ambientes(descripcion) Select distinct ambientes from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN ambientes_id INTEGER;
UPDATE inmuebles SET ambientes_id = (Select id from ambientes where descripcion = inmuebles.ambientes);
ALTER TABLE inmuebles DROP COLUMN ambientes;

---------------
UPDATE inmuebles SET dormitorios = 'Sin información' where dormitorios is null;
CREATE TABLE dormitorios (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO dormitorios(descripcion) Select distinct dormitorios from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN dormitorios_id INTEGER;
UPDATE inmuebles SET dormitorios_id = (Select id from dormitorios where descripcion = inmuebles.dormitorios);
ALTER TABLE inmuebles DROP COLUMN dormitorios;

---------------
UPDATE inmuebles SET garages = 'Sin información' where garages is null;
CREATE TABLE garages (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO garages(descripcion) Select distinct garages from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN garages_id INTEGER;
UPDATE inmuebles SET garages_id = (Select id from garages where descripcion = inmuebles.garages);
ALTER TABLE inmuebles DROP COLUMN garages;

---------------
UPDATE inmuebles SET orientacion = 'Sin información' where orientacion is null;
CREATE TABLE orientacion (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO orientacion(descripcion) Select distinct orientacion from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN orientacion_id INTEGER;
UPDATE inmuebles SET orientacion_id = (Select id from orientacion where descripcion = inmuebles.orientacion);
ALTER TABLE inmuebles DROP COLUMN orientacion;


---------------
UPDATE inmuebles SET departamento = 'Sin información' where departamento is null;
CREATE TABLE departamento (
    "id"	INTEGER NOT NULL,
    "descripcion"	INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO departamento(descripcion) Select distinct departamento from inmuebles order by 1;
ALTER TABLE inmuebles ADD COLUMN departamento_id INTEGER;
UPDATE inmuebles SET departamento_id = (Select id from departamento where descripcion = inmuebles.departamento);
ALTER TABLE inmuebles DROP COLUMN departamento;

---------------

ALTER TABLE categoria ADD COLUMN escala INTEGER;
ALTER TABLE antiguedad ADD COLUMN escala INTEGER;
ALTER TABLE banos ADD COLUMN escala INTEGER;
ALTER TABLE ambientes ADD COLUMN escala INTEGER;
ALTER TABLE dormitorios ADD COLUMN escala INTEGER;
ALTER TABLE garages ADD COLUMN escala INTEGER;
-- ALTER TABLE orientacion ADD COLUMN escala INTEGER;
-- ALTER TABLE departamento ADD COLUMN escala INTEGER;

---------------

CREATE VIEW vista_inmuebles AS
SELECT
    i.precio,
    i.publicacion,
    i.visitas,
    i.anuncio_id,
    i.superficie_total,
    i.superficie_cubierta,
    i.apto_credito,
    i.en_barrio_privado,
    i.latitude,
    i.longitude,
    i.image_blob,
    i.categoria_id,
    ant.escala as antiguedad_escala,
    ban.escala as banos_escala,
    amb.escala as ambientes_escala,
    dor.escala as dormitorios_escala,
    gar.escala as garages_escala,
    i.orientacion_id,
    i.departamento_id,
    i.superficie_total_m2,
    i.superficie_cubierta_m2,
    i.comentarios
FROM inmuebles i
INNER JOIN antiguedad ant ON ant.id = i.antiguedad_id
INNER JOIN banos ban ON ban.id = i.banos_id
INNER JOIN ambientes amb ON amb.id = i.ambientes_id
INNER JOIN dormitorios dor ON dor.id = i.dormitorios_id
INNER JOIN garages gar ON gar.id = i.garages_id;