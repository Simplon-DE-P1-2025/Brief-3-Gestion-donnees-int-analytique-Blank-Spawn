-- Nombre total d’opération
SELECT COUNT(operation_id) AS nb_operations
FROM operation;

--Durée moyenne d’une opération(a teste)
SELECT
    AVG(date_heure_fin_operation - date_heure_reception_alerte) AS duree_moyenne
FROM operation
WHERE date_heure_fin_operation IS NOT NULL;

--Répartition des opérations par type
SELECT type_operation, COUNT(operation_id) AS nb
FROM operation
GROUP BY type_operation
ORDER BY nb DESC;

--Taux de blessés (a tester)
SELECT
    ROUND(
        SUM(dont_nombre_blesse)::NUMERIC
        / NULLIF(SUM(nombre), 0)
        * 100,
        2
    ) AS taux_blesses_pourcent
FROM resultats_humain;

--Opérations en conditions météo difficiles
SELECT COUNT(operation_id) AS nb_operations_difficiles
FROM operation
WHERE vent_force >= 6
   OR mer_force >= 5;

--Impact humain vs météo
SELECT
    CASE
        WHEN vent_force >= 6 OR mer_force >= 5 THEN 'Conditions difficiles'
        ELSE 'Conditions normales'
    END AS conditions,
    SUM(r.nombre) AS personnes_impliquees,
    SUM(r.dont_nombre_blesse) AS blesses
FROM operation o
JOIN resultats_humain r ON o.operation_id = r.operation_id
GROUP BY conditions;

--Résultat des flotteurs
SELECT resultat_flotteur, COUNT(*) AS nb
FROM flotteurs
GROUP BY resultat_flotteur
ORDER BY nb DESC;

--Activité par département
SELECT departement, COUNT(*) AS nb_operations
FROM operation
GROUP BY departement
ORDER BY nb_operations DESC;

--Opérations métropolitaines vs hors métropole
SELECT est_metropolitain, COUNT(*) AS nb
FROM operation
GROUP BY est_metropolitain;

--Opérations avec impact humain
SELECT COUNT(DISTINCT o.operation_id) AS operations_avec_personnes
FROM operation o
JOIN resultats_humain r ON o.operation_id = r.operation_id
WHERE r.nombre > 0;

--Nombre moyen de personnes par opération
SELECT AVG(total_personnes) AS moyenne_personnes
FROM (
    SELECT operation_id, SUM(nombre) AS total_personnes
    FROM resultats_humain
    GROUP BY operation_id
) t;