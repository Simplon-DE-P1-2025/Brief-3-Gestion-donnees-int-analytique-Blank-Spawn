-- =====================================================
-- Table : operation
-- =====================================================
CREATE TABLE IF NOT EXISTS operation (
    operation_id VARCHAR(50) PRIMARY KEY, -- operation_pkey
    type_operation VARCHAR(5),
    pourquoi_alerte VARCHAR(50),
    moyen_alerte VARCHAR(50),
    qui_alerte VARCHAR(50),
    categorie_qui_alerte VARCHAR(50),
    cross_type VARCHAR(50),
    departement VARCHAR(50),
    est_metropolitain BOOLEAN,
    evenement VARCHAR(50),
    categorie_evenement VARCHAR(50),
    autorite VARCHAR(50),
    seconde_autorite VARCHAR(50),
    zone_responsabilite VARCHAR(50),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    vent_direction INTEGER CHECK (vent_direction BETWEEN 0 AND 360),
    vent_direction_categorie VARCHAR(50),
    vent_force INTEGER CHECK (vent_force BETWEEN 0 AND 12),
    mer_force INTEGER CHECK (mer_force BETWEEN 0 AND 9),
    date_heure_reception_alerte TIMESTAMP,
    date_heure_fin_operation TIMESTAMP,
    numero_sitrep VARCHAR(50),
    cross_sitrep VARCHAR(50),
    fuseau_horaire VARCHAR(50),
    systeme_source VARCHAR(50)
);

-- =====================================================
-- Table : flotteurs (WITH unique ID)
-- =====================================================
CREATE TABLE IF NOT EXISTS flotteurs (
    flotteur_id BIGSERIAL PRIMARY KEY,
    operation_id VARCHAR(50) NOT NULL,
    numero_ordre INTEGER,
    pavillon VARCHAR(10),
    resultat_flotteur VARCHAR(50),
    type_flotteur VARCHAR(50),
    categorie_flotteur VARCHAR(30),
    numero_immatriculation VARCHAR(60),

    CONSTRAINT flotteurs_unique
        UNIQUE (operation_id, numero_ordre),

    CONSTRAINT fk_flotteurs_operation
        FOREIGN KEY (operation_id)
        REFERENCES operation (operation_id)
        ON DELETE CASCADE
);

-- =====================================================
-- Table : resultats_humain (WITH unique ID)
-- =====================================================
CREATE TABLE IF NOT EXISTS resultats_humain (
    resultat_id BIGSERIAL PRIMARY KEY,
    operation_id VARCHAR(50) NOT NULL,
    categorie_personne VARCHAR(100),
    resultat_humain VARCHAR(70),
    nombre INTEGER,
    dont_nombre_blesse INTEGER,

    CONSTRAINT resultats_humain_unique
        UNIQUE (operation_id, categorie_personne),

    CONSTRAINT fk_resultats_humain_operation
        FOREIGN KEY (operation_id)
        REFERENCES operation (operation_id)
        ON DELETE CASCADE
);
