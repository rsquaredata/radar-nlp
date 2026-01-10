
-- Suppression des tables si elles existent
DROP TABLE IF EXISTS fact_offer_skill;
DROP TABLE IF EXISTS fact_offers;
DROP TABLE IF EXISTS dim_source;
DROP TABLE IF EXISTS dim_region;
DROP TABLE IF EXISTS dim_company;
DROP TABLE IF EXISTS dim_contract;
DROP TABLE IF EXISTS dim_skill;
DROP TABLE IF EXISTS dim_date;



-- Dimension : Sources de données
CREATE TABLE dim_source (
    source_key INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL UNIQUE,
    source_type TEXT,  -- 'api', 'scraping', 'manual'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension : Régions françaises
CREATE TABLE dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension : Entreprises
CREATE TABLE dim_company (
    company_key INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension : Types de contrat
CREATE TABLE dim_contract (
    contract_key INTEGER PRIMARY KEY AUTOINCREMENT,
    contract_type TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension : Compétences
CREATE TABLE dim_skill (
    skill_key INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL UNIQUE,
    skill_type TEXT CHECK(skill_type IN ('competences', 'savoir_etre')),
    skill_category TEXT,  -- 'languages', 'cloud', 'communication', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Dimension : Dates (pour analyses temporelles)
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY AUTOINCREMENT,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    quarter INTEGER,
    week_of_year INTEGER,
    day_of_week INTEGER,
    month_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE fact_offers (
    offer_key INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- ⭐ CONTRAINTE UNICITÉ : uid est unique (évite doublons)
    uid TEXT NOT NULL UNIQUE,
    offer_id TEXT NOT NULL,
    
    -- Clés étrangères vers dimensions
    source_key INTEGER,
    region_key INTEGER,
    company_key INTEGER,
    contract_key INTEGER,
    date_key INTEGER,
    
    -- Attributs de l'offre
    title TEXT NOT NULL,
    source_url TEXT,
    location TEXT,
    salary TEXT,
    remote TEXT,
    published_date TEXT,
    description TEXT,
    
    -- Métriques dérivées
    skills_count INTEGER DEFAULT 0,
    competences_count INTEGER DEFAULT 0,
    savoir_etre_count INTEGER DEFAULT 0,
    
    -- ⭐ Métadonnées de traçabilité
    added_by TEXT DEFAULT 'import',  -- 'import', 'manual', 'scraping_streamlit'
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Clés étrangères
    FOREIGN KEY (source_key) REFERENCES dim_source(source_key),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key),
    FOREIGN KEY (company_key) REFERENCES dim_company(company_key),
    FOREIGN KEY (contract_key) REFERENCES dim_contract(contract_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);



-- Relation offre ↔ compétence
CREATE TABLE fact_offer_skill (
    offer_key INTEGER NOT NULL,
    skill_key INTEGER NOT NULL,
    
    PRIMARY KEY (offer_key, skill_key),
    FOREIGN KEY (offer_key) REFERENCES fact_offers(offer_key) ON DELETE CASCADE,
    FOREIGN KEY (skill_key) REFERENCES dim_skill(skill_key) ON DELETE CASCADE
);



-- ⭐ Index UNIQUE sur uid (évite doublons)
CREATE UNIQUE INDEX idx_fact_offers_uid_unique ON fact_offers(uid);

-- Index sur les clés étrangères
CREATE INDEX idx_fact_offers_source ON fact_offers(source_key);
CREATE INDEX idx_fact_offers_region ON fact_offers(region_key);
CREATE INDEX idx_fact_offers_company ON fact_offers(company_key);
CREATE INDEX idx_fact_offers_contract ON fact_offers(contract_key);
CREATE INDEX idx_fact_offers_date ON fact_offers(date_key);

-- Index sur fact_offer_skill
CREATE INDEX idx_fact_offer_skill_offer ON fact_offer_skill(offer_key);
CREATE INDEX idx_fact_offer_skill_skill ON fact_offer_skill(skill_key);

-- Index sur dim_skill pour recherches
CREATE INDEX idx_dim_skill_type ON dim_skill(skill_type);
CREATE INDEX idx_dim_skill_category ON dim_skill(skill_category);

-- Index sur fact_offers pour recherches
CREATE INDEX idx_fact_offers_title ON fact_offers(title);
CREATE INDEX idx_fact_offers_location ON fact_offers(location);

-- ============================================================================
-- VUES UTILES
-- ============================================================================

-- Vue : Offres avec toutes les dimensions
CREATE VIEW v_offers_complete AS
SELECT 
    fo.offer_key,
    fo.uid,
    fo.title,
    fo.location,
    fo.salary,
    fo.remote,
    fo.description,
    fo.skills_count,
    fo.competences_count,
    fo.savoir_etre_count,
    fo.added_by,
    fo.added_at,
    ds.source_name,
    dr.region_name,
    dr.latitude,
    dr.longitude,
    dc.company_name,
    dct.contract_type,
    dd.full_date AS published_date,
    fo.source_url
FROM fact_offers fo
LEFT JOIN dim_source ds ON fo.source_key = ds.source_key
LEFT JOIN dim_region dr ON fo.region_key = dr.region_key
LEFT JOIN dim_company dc ON fo.company_key = dc.company_key
LEFT JOIN dim_contract dct ON fo.contract_key = dct.contract_key
LEFT JOIN dim_date dd ON fo.date_key = dd.date_key;

-- Vue : Top compétences
CREATE VIEW v_top_skills AS
SELECT 
    ds.skill_name,
    ds.skill_type,
    ds.skill_category,
    COUNT(DISTINCT fos.offer_key) AS offer_count,
    ROUND(COUNT(DISTINCT fos.offer_key) * 100.0 / (SELECT COUNT(*) FROM fact_offers), 2) AS percentage
FROM dim_skill ds
JOIN fact_offer_skill fos ON ds.skill_key = fos.skill_key
GROUP BY ds.skill_key, ds.skill_name, ds.skill_type, ds.skill_category
ORDER BY offer_count DESC;

-- Vue : Offres par région
CREATE VIEW v_offers_by_region AS
SELECT 
    dr.region_name,
    dr.latitude,
    dr.longitude,
    COUNT(fo.offer_key) AS offer_count,
    AVG(fo.skills_count) AS avg_skills_per_offer
FROM dim_region dr
LEFT JOIN fact_offers fo ON dr.region_key = fo.region_key
GROUP BY dr.region_key, dr.region_name, dr.latitude, dr.longitude
ORDER BY offer_count DESC;

-- Vue : Compétences par offre
CREATE VIEW v_offer_skills AS
SELECT 
    fo.offer_key,
    fo.uid,
    fo.title,
    ds.skill_name,
    ds.skill_type,
    ds.skill_category
FROM fact_offers fo
JOIN fact_offer_skill fos ON fo.offer_key = fos.offer_key
JOIN dim_skill ds ON fos.skill_key = ds.skill_key;

-- Vue : Statistiques globales
CREATE VIEW v_stats_global AS
SELECT 
    (SELECT COUNT(*) FROM fact_offers) AS total_offers,
    (SELECT COUNT(DISTINCT region_key) FROM fact_offers WHERE region_key IS NOT NULL) AS total_regions,
    (SELECT COUNT(*) FROM dim_skill) AS total_skills,
    (SELECT COUNT(*) FROM dim_skill WHERE skill_type = 'competences') AS total_competences,
    (SELECT COUNT(*) FROM dim_skill WHERE skill_type = 'savoir_etre') AS total_savoir_etre,
    (SELECT AVG(skills_count) FROM fact_offers) AS avg_skills_per_offer;


CREATE TRIGGER update_fact_offers_timestamp 
AFTER UPDATE ON fact_offers
BEGIN
    UPDATE fact_offers 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE offer_key = NEW.offer_key;
END;

