"""
Générateur des jeux de données synthétiques du Module 10 (PIIA · AMA).

- etudiants.csv   : 320 étudiants fictifs (notes, heures d'étude, présence...) — utilisé dans le cours
- filieres.csv    : table de référence des filières (pour les jointures)
- ventes.csv      : ~12 000 transactions 2025 d'une chaîne fictive de supermarchés "MarchéPlus" — mini-projet
- produits.csv    : catalogue produits (prix en FCFA)
- magasins.csv    : liste des magasins

Les données contiennent volontairement des défauts (valeurs manquantes, doublons,
fautes de saisie, valeurs aberrantes) pour pratiquer le nettoyage.

Usage :  python generer_donnees.py   (écrit les fichiers dans ./data)
"""
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# 1. Étudiants (cours)
# ---------------------------------------------------------------------------
def generer_etudiants(n: int = 320, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    filieres = np.array(["Maths", "Informatique", "Économie", "Physique"])
    villes = np.array(["Cotonou", "Porto-Novo", "Abomey-Calavi", "Parakou", "Bohicon"])

    filiere = rng.choice(filieres, n, p=[0.25, 0.35, 0.25, 0.15])
    ville = rng.choice(villes, n, p=[0.35, 0.15, 0.25, 0.15, 0.10])
    sexe = rng.choice(["F", "M"], n, p=[0.45, 0.55])
    age = rng.integers(19, 33, n)
    heures = rng.gamma(4, 2.5, n).round(1)                       # heures d'étude / semaine
    presence = np.clip(rng.normal(80, 12, n), 30, 100).round(0)  # taux de présence en %
    bonus = pd.Series(filiere).map({"Maths": 1.0, "Informatique": 0.6,
                                    "Économie": 0.0, "Physique": 0.8}).to_numpy()

    note_python = np.clip(2 + 0.45 * heures + 0.06 * presence + bonus + rng.normal(0, 2, n), 0, 20)
    note_stats = np.clip(0.55 * note_python + 0.1 * heures + rng.normal(4, 2.2, n), 0, 20)
    note_algebre = np.clip(0.4 * note_stats + 0.3 * note_python + rng.normal(3.5, 2.5, n) + bonus, 0, 20)

    debut = np.datetime64("2026-03-01")
    date_insc = debut + rng.integers(0, 150, n).astype("timedelta64[D]")

    df = pd.DataFrame({
        "id_etudiant": [f"E{i:03d}" for i in range(1, n + 1)],
        "sexe": sexe,
        "age": age,
        "ville": ville,
        "filiere": filiere,
        "heures_etude": heures,
        "taux_presence": presence,
        "note_python": note_python.round(1),
        "note_stats": note_stats.round(1),
        "note_algebre": note_algebre.round(1),
        "date_inscription": pd.to_datetime(date_insc).strftime("%Y-%m-%d"),
    })

    # --- défauts volontaires ---
    idx = rng.choice(n, 18, replace=False)
    df.loc[idx[:10], "heures_etude"] = np.nan
    df.loc[idx[10:], "note_stats"] = np.nan
    idx = rng.choice(n, 25, replace=False)
    df.loc[idx[:10], "ville"] = df.loc[idx[:10], "ville"].str.upper()
    df.loc[idx[10:], "ville"] = df.loc[idx[10:], "ville"].str.lower() + " "
    df = pd.concat([df, df.sample(6, random_state=seed)], ignore_index=True)  # doublons
    return df


def generer_filieres() -> pd.DataFrame:
    return pd.DataFrame({
        "filiere": ["Maths", "Informatique", "Économie", "Physique", "Biologie"],
        "departement": ["Sciences", "Sciences & Tech.", "Sciences Sociales", "Sciences", "Sciences de la Vie"],
        "frais_annuels_fcfa": [250_000, 350_000, 225_000, 250_000, 275_000],
        "duree_ans": [3, 3, 3, 3, 3],
    })


# ---------------------------------------------------------------------------
# 2. MarchéPlus (mini-projet)
# ---------------------------------------------------------------------------
PRODUITS = [
    # nom, catégorie, prix FCFA, popularité
    ("Riz parfumé 5 kg", "Alimentation", 4500, 9), ("Huile végétale 1 L", "Alimentation", 1300, 8),
    ("Sucre en poudre 1 kg", "Alimentation", 800, 7), ("Gari 1 kg", "Alimentation", 600, 8),
    ("Tomate concentrée 400 g", "Alimentation", 700, 7), ("Lait en poudre 400 g", "Alimentation", 2500, 5),
    ("Spaghetti 500 g", "Alimentation", 450, 8), ("Farine de blé 1 kg", "Alimentation", 700, 4),
    ("Eau minérale 1,5 L", "Boissons", 400, 10), ("Soda 33 cl", "Boissons", 400, 8),
    ("Jus d'ananas 1 L", "Boissons", 1200, 5), ("Bière 65 cl", "Boissons", 700, 7),
    ("Malt 33 cl", "Boissons", 500, 4),
    ("Savon de toilette", "Hygiène", 350, 7), ("Dentifrice 100 ml", "Hygiène", 900, 5),
    ("Lessive 1 kg", "Hygiène", 1500, 5), ("Papier toilette x4", "Hygiène", 1200, 4),
    ("Crème corporelle", "Hygiène", 2800, 3),
    ("Écouteurs filaires", "Électronique", 3500, 2), ("Chargeur USB-C", "Électronique", 4000, 2),
    ("Batterie externe 10 000 mAh", "Électronique", 12000, 1), ("Ampoule LED", "Électronique", 1500, 3),
    ("Ventilateur de table", "Électronique", 18000, 1),
    ("Seau 15 L", "Maison", 2000, 2), ("Balai", "Maison", 1000, 3),
    ("Assiettes x6", "Maison", 5000, 1), ("Moustiquaire", "Maison", 6500, 2),
]

MAGASINS = [
    # id, ville, quartier, surface m², ouverture, poids trafic, biais satisfaction
    ("M01", "Cotonou", "Ganhi", 1800, "2016-03-15", 0.26, 0.2),
    ("M02", "Cotonou", "Fidjrossè", 700, "2019-10-01", 0.18, 0.0),
    ("M03", "Abomey-Calavi", "Godomey", 1100, "2020-06-20", 0.19, 0.1),
    ("M04", "Porto-Novo", "Ouando", 650, "2018-01-10", 0.13, -0.9),
    ("M05", "Parakou", "Zongo", 950, "2021-09-05", 0.14, 0.1),
    ("M06", "Bohicon", "Centre", 400, "2023-04-12", 0.10, 0.0),
]


def generer_marcheplus(n: int = 12_000, seed: int = 2025):
    rng = np.random.default_rng(seed)

    produits = pd.DataFrame(PRODUITS, columns=["nom_produit", "categorie", "prix_unitaire", "_pop"])
    produits.insert(0, "id_produit", [f"P{i:03d}" for i in range(1, len(produits) + 1)])
    magasins = pd.DataFrame(MAGASINS, columns=["id_magasin", "ville", "quartier", "surface_m2",
                                                "date_ouverture", "_poids", "_satisf"])

    # --- dates : saisonnalité mensuelle + effet week-end ---
    jours = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    f_mois = np.array([0.85, 0.85, 0.95, 1.0, 0.95, 0.9, 0.95, 1.1, 1.05, 1.0, 1.1, 1.55])
    f_jour = np.array([0.9, 0.85, 0.9, 0.95, 1.1, 1.45, 1.2])  # lun..dim
    poids = f_mois[jours.month - 1] * f_jour[jours.dayofweek]
    date = jours[rng.choice(len(jours), n, p=poids / poids.sum())]

    # heures : deux pics (midi et fin de journée)
    heure = np.where(rng.random(n) < 0.35, rng.normal(12.5, 1.3, n), rng.normal(18, 1.6, n))
    heure = np.clip(heure, 8, 21.9)
    minutes = (heure % 1 * 60).astype(int)
    date = date + pd.to_timedelta(heure.astype(int), unit="h") + pd.to_timedelta(minutes, unit="m")

    mag_idx = rng.choice(len(magasins), n, p=magasins["_poids"] / magasins["_poids"].sum())
    prod_idx = rng.choice(len(produits), n, p=produits["_pop"] / produits["_pop"].sum())
    cat = produits["categorie"].to_numpy()[prod_idx]

    quantite = np.where(np.isin(cat, ["Électronique", "Maison"]), 1, rng.poisson(1.6, n) + 1)

    # paiement : le Mobile Money progresse au fil de l'année, la carte surtout à Cotonou
    mois = date.month.to_numpy()
    p_mm = 0.22 + 0.025 * mois
    p_carte = np.where(np.isin(mag_idx, [0, 1]), 0.14, 0.05)
    u = rng.random(n)
    paiement = np.where(u < p_mm, "Mobile Money", np.where(u < p_mm + p_carte, "Carte", "Espèces"))

    age = np.clip(rng.normal(33, 10, n), 16, 75).round(0)
    # les plus jeunes achètent plus d'électronique
    jeunes = np.isin(cat, ["Électronique"])
    age[jeunes] = np.clip(rng.normal(26, 6, jeunes.sum()), 16, 60).round(0)
    sexe = rng.choice(["F", "M"], n, p=[0.56, 0.44])

    remise = rng.choice([0, 5, 10, 15], n, p=[0.8, 0.1, 0.07, 0.03])
    dec = mois == 12
    remise[dec] = rng.choice([0, 5, 10, 15], dec.sum(), p=[0.5, 0.2, 0.2, 0.1])
    quantite = quantite + (remise >= 10) * rng.integers(0, 3, n)

    satisf = 3.6 + magasins["_satisf"].to_numpy()[mag_idx] + rng.normal(0, 0.9, n) + (heure > 18.5) * -0.3
    satisf = np.clip(np.round(satisf), 1, 5)

    ventes = pd.DataFrame({
        "id_transaction": [f"T{i:05d}" for i in range(1, n + 1)],
        "date_heure": date.strftime("%Y-%m-%d %H:%M"),
        "id_magasin": magasins["id_magasin"].to_numpy()[mag_idx],
        "id_produit": produits["id_produit"].to_numpy()[prod_idx],
        "quantite": quantite,
        "remise_pct": remise,
        "mode_paiement": paiement,
        "age_client": age,
        "sexe_client": sexe,
        "satisfaction": satisf,
    }).sort_values("date_heure", ignore_index=True)
    ventes["id_transaction"] = [f"T{i:05d}" for i in range(1, n + 1)]

    # --- défauts volontaires ---
    r = np.random.default_rng(seed + 1)
    i = r.choice(n, 450, replace=False)
    ventes.loc[i[:120], "mode_paiement"] = ventes.loc[i[:120], "mode_paiement"].str.lower()
    ventes.loc[i[120:170], "mode_paiement"] = ventes.loc[i[120:170], "mode_paiement"].replace(
        {"Mobile Money": "MoMo", "Espèces": "especes", "Carte": "CB"})
    ventes.loc[i[170:420], "age_client"] = np.nan
    ventes.loc[i[420:435], "quantite"] = -ventes.loc[i[420:435], "quantite"]      # retours / erreurs
    ventes.loc[i[435:440], "quantite"] = [250, 400, 300, 500, 350]                 # fautes de frappe
    ventes.loc[i[440:450], "satisfaction"] = np.nan
    ventes = pd.concat([ventes, ventes.sample(40, random_state=1)]).sort_values("date_heure", ignore_index=True)

    produits = produits.drop(columns="_pop")
    magasins = magasins.drop(columns=["_poids", "_satisf"])
    return ventes, produits, magasins


def generer_tout(dossier="data") -> None:
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    generer_etudiants().to_csv(dossier / "etudiants.csv", index=False)
    generer_filieres().to_csv(dossier / "filieres.csv", index=False)
    ventes, produits, magasins = generer_marcheplus()
    ventes.to_csv(dossier / "ventes.csv", index=False)
    produits.to_csv(dossier / "produits.csv", index=False)
    magasins.to_csv(dossier / "magasins.csv", index=False)
    print(f"Fichiers générés dans {dossier.resolve()}")


if __name__ == "__main__":
    generer_tout()
