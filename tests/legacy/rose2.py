# -*- coding: utf-8 -*-
# =============================================================================
#  ADS kūrybinė užduotis: du 3D modeliai iš parametrinių paviršių ir sukinių
#
#    1) "100 rožių"       ->  100_roziu.off        (vyro dovana mylimajai)
#    2) "3 rožės vazoje"  ->  3_rozes_vazoje.off
#
#  Programa naudoja TIK add.py (v1.2b) modulį:
#     parametric(...) - parametriniai paviršiai (rožės žiedas, lapai,
#                       žiedlapiai, klostuotas vyniojamasis popierius, kaspinas),
#     spin3D(...)     - SUKINIAI (vaza, žiedo taurelė, popieriaus piltuvas,
#                       kaspino mazgas - toras),
#     curve(...)      - parametrinės 3D kreivės (stiebai - kubinės Bezjė kreivės
#                       su kintančiu spinduliu),
#     cylinder/cone   - stalviršis, vanduo, spygliai, lapkočiai, gyslos,
#     layer, mesh, merge, move, rotateX/Y/Z, zoom, center
#                     - sluoksniai: vienas rožės tinklas panaudojamas 100 kartų.
#
#  VISI PARAMETRINIAI PAVIRŠIAI YRA TŪRINIAI (žr. 2 dalį):
#     paviršius S(u,v) "išpučiamas" į uždarą apvalkalą - dvi kopijos, pastumtos
#     per +storis/2 ir -storis/2 paviršiaus normalės kryptimi, plius kraštų
#     juostos. Todėl kiekviena siena turi teisingai (prieš laikrodžio rodyklę
#     iš išorės) išdėstytas viršūnes ir modelis vienodai apšviestas iš visų
#     pusių - ir iš viršaus, ir iš apačios.
#
#  MODELIO FORMĄ VALDANTYS PARAMETRAI (pakeitus - keičiasi visas modelis):
#     PETALS  - žiedlapių tankumas (kiek žiedlapių viename apsisukime),
#     DECAY   - kaip greitai žiedas atsiveria (mažesnis -> plokštesnė rožė),
#     CURL    - žiedlapio krašto užsirietimas,
#     THETA_MAX - kiek žiedlapių eilių turi rožė,
#     STORIS  - žiedlapių ir lapų storis,
#     DETALUMAS - tinklo tankumas (daugiakampių skaičius),
#     N       - rožių skaičius pirmame modelyje.
# =============================================================================

import math
import random
import add

TAU = 2.0 * math.pi
random.seed(2026)                 # kad rezultatas visada būtų vienodas


def pw(x, p):
    """Laipsnis, apsaugotas nuo neigiamos bazės (normalė skaičiuojama ir
       šiek tiek už paviršiaus krašto, todėl x gali būti truputį < 0)."""
    return math.pow(x, p) if x > 0.0 else 0.0

# ---------------- pagrindiniai rožės formos parametrai -----------------------
PETALS = 3.6                      # žiedlapių per apsisukimą
DECAY = 8.0                       # žiedo atsivėrimo greitis
CURL = 1.3                        # žiedlapio užsirietimas
THETA_MIN = -2.0 * math.pi
THETA_MAX = 15.0 * math.pi
STORIS = 0.030                    # žiedlapio storis (prie žiedo pagrindo)


# =============================================================================
#  1 DALIS.  PARAMETRINIAI PAVIRŠIAI  S(u,v) = [x, y, z]
# =============================================================================

# -----------------------------------------------------------------------------
#  ROŽĖS ŽIEDAS.  u = theta (sukimosi kampas), v = r (atstumas žiedlapiu)
#
#     fi(u)    = (pi/2) * e^(-u/(DECAY*pi))                     - atsivėrimas
#     X(u)     = 1 - 1/2*( 5/4*(1 - ((PETALS*u) mod 2pi)/pi)^2 - 1/4 )^2
#     y(u,v)   = 2*v^2*(CURL*v - 1)^2 * sin(fi)                 - užsirietimas
#     rho(u,v) = X * ( v*sin(fi) + y*cos(fi) )                  - iki ašies
#     h(u,v)   = X * ( v*cos(fi) - y*sin(fi) )                  - aukštis
#
#     (x, y, z) = ( rho*sin(u),  h,  rho*cos(u) )     (Y ašis - aukštis)
# -----------------------------------------------------------------------------
def ziedo_pavirsius(petals=PETALS, decay=DECAY, curl=CURL):
    def S(u, v):
        fi = (math.pi / 2.0) * math.exp(-u / (decay * math.pi))
        m = ((petals * u) % TAU) / math.pi
        X = 1.0 - 0.5 * (1.25 * (1.0 - m) ** 2 - 0.25) ** 2
        y = 2.0 * v * v * (curl * v - 1.0) ** 2 * math.sin(fi)
        rho = X * (v * math.sin(fi) + y * math.cos(fi))
        h = X * (v * math.cos(fi) - y * math.sin(fi))
        return [rho * math.sin(u), h, rho * math.cos(u)]
    return S


# -----------------------------------------------------------------------------
#  LAPAS (ta pati lygtis naudojama ir žiedlapiams, sepalams, kaspino galams)
#     u in [0,1]  - nuo lapo pagrindo iki smaigalio,
#     v in [-1,1] - skersai lapo.
#
#     w(u) = W*sin(pi*u^p)*(1 + zub*sin(dant*pi*u))   - pusplotis (dantytas)
#     x = L*u
#     y = -sag*u^2 + fold*w*v^2 + tw*u*v*w            - nuolydis, lovelis, sukimas
#     z = w*v
# -----------------------------------------------------------------------------
def lapo_pavirsius(L=1.0, W=0.35, p=0.7, sag=0.25, fold=0.55, tw=0.15,
                   zub=0.10, dant=13.0):
    def S(u, v):
        w = W * math.sin(math.pi * pw(u, p)) * (1.0 + zub * math.sin(dant * math.pi * u))
        return [L * u,
                -sag * u * u + fold * w * v * v + tw * u * v * w,
                w * v]
    return S


# -----------------------------------------------------------------------------
#  VYNIOJAMASIS POPIERIUS - klostuotas kūginis paviršius
#     u in [0,2pi] - kampas,  v in [0,1] - nuo smaigalio iki krašto
# -----------------------------------------------------------------------------
def popieriaus_pavirsius(r0, r1, y0, y1, klosciu=11, gylis=0.09, banga=0.55):
    def S(u, v):
        k = 1.0 + gylis * math.sin(klosciu * u)
        r = (r0 + (r1 - r0) * pw(v, 0.75)) * k
        y = y0 + (y1 - y0) * v + banga * v ** 3 * math.sin(klosciu * u)
        return [r * math.cos(u), y, r * math.sin(u)]
    return S


def popieriaus_r(y, r0, r1, y0, y1, gylis=0.10):
    """Didžiausias klostuoto popieriaus spindulys aukštyje y."""
    v = min(1.0, max(0.0, (y - y0) / (y1 - y0)))
    return (r0 + (r1 - r0) * pw(v, 0.75)) * (1.0 + gylis)


# -----------------------------------------------------------------------------
#  KASPINO JUOSTA - banguota juosta, apjuosianti kūgį
#     u in [0,2pi] - kampas, v in [0,1] - nuo apatinio iki viršutinio krašto
# -----------------------------------------------------------------------------
def kaspino_pavirsius(rb, rt, yb, yt, banguot=0.25, n=7):
    def S(u, v):
        b = math.sin(n * u)
        r = rb + (rt - rb) * v + 0.10 * b
        y = yb + (yt - yb) * v + banguot * b
        return [r * math.cos(u), y, r * math.sin(u)]
    return S


# =============================================================================
#  2 DALIS.  TŪRINIAI (DVIPUSIAI) PARAMETRINIAI PAVIRŠIAI
#
#  Parametrinis paviršius pats savaime yra be tūrio: jo sienos apšviestos tik
#  iš vienos pusės. Todėl kiekvienas paviršius S(u,v) čia paverčiamas UŽDARU
#  APVALKALU (kaip tikras žiedlapis ar lapas, turintis storį):
#
#     n(u,v)  - paviršiaus normalė (vienetinis vektorius),
#     S+(u,v) = S(u,v) + n*storis/2      - viršutinė pusė,
#     S-(u,v) = S(u,v) - n*storis/2      - apatinė pusė (u kryptis apsukama,
#                                          todėl jos sienos atsuktos į išorę),
#     kraštų juostos                     - sujungia abi puses į uždarą tūrį.
#
#  Kadangi abu apvalkalai atsukti nuo vidurinio paviršiaus, sienų viršūnės
#  visada išdėstytos prieš laikrodžio rodyklę žiūrint IŠ IŠORĖS - modelis
#  taisyklingai apšviestas iš visų pusių.
# =============================================================================

def normale(S, u, v, hu, hv):
    """Parametrinio paviršiaus vienetinė normalė n = Su x Sv (skaitiniu būdu).
       hu, hv - TINKLO žingsniai: taip gauname vidutinę tinklo langelių normalę,
       ir abu pastumti apvalkalai niekur nesusikerta (net kai tinklas retas)."""
    a, b = S(u + hu, v), S(u - hu, v)
    c, d = S(u, v + hv), S(u, v - hv)
    du = [a[i] - b[i] for i in range(3)]
    dv = [c[i] - d[i] for i in range(3)]
    n = [du[1] * dv[2] - du[2] * dv[1],
         du[2] * dv[0] - du[0] * dv[2],
         du[0] * dv[1] - du[1] * dv[0]]
    m = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2)
    if m < 1e-12:                       # išsigimęs taškas (pvz. ašis)
        return [0.0, 0.0, 0.0]
    return [n[0] / m, n[1] / m, n[2] / m]


def _storis(st, u, v):
    return st(u, v) if callable(st) else st


def paslinktas(S, st, s, hu, hv):
    """Paviršius, pastumtas per s*storis/2 normalės kryptimi (s = +1 arba -1)."""
    def F(u, v):
        p = S(u, v)
        n = normale(S, u, v, hu, hv)
        d = 0.5 * s * _storis(st, u, v)
        return [p[i] + n[i] * d for i in range(3)]
    return F


def _riba(S, st, fiks, ar_u, hu, hv):
    """Krašto juosta: w in [0,1] veda nuo viršutinės pusės prie apatinės.
       ar_u=True - kraštas, kuriame u=fiks (bėgantis parametras v),
       ar_u=False - kraštas, kuriame v=fiks (bėgantis parametras u)."""
    def B(a, w):
        u, v = (fiks, a) if ar_u else (a, fiks)
        p = S(u, v)
        n = normale(S, u, v, hu, hv)
        d = (0.5 - w) * _storis(st, u, v)
        return [p[i] + n[i] * d for i in range(3)]
    return B


def pav_su_storiu(S, u0, u1, gu, v0, v1, gv, st, RGB,
                  krastai=(False, False, False, False), gw=1):
    """Tūrinis parametrinis paviršius. krastai = (u0, u1, v0, v1) - kuriuos
       kraštus užsandarinti (išsigimusių kraštų sandarinti nereikia)."""
    hu = (u1 - u0) / gu                 # tinklo žingsniai
    hv = (v1 - v0) / gv
    add.parametric(paslinktas(S, st, +1, hu, hv), u0, u1, gu, v0, v1, gv, RGB)
    add.parametric(paslinktas(S, st, -1, hu, hv), u1, u0, gu, v0, v1, gv, RGB)
    if krastai[0]:
        add.parametric(_riba(S, st, u0, True, hu, hv), v0, v1, gv, 0, 1, gw, RGB)
    if krastai[1]:
        add.parametric(_riba(S, st, u1, True, hu, hv), v0, v1, gv, 1, 0, gw, RGB)
    if krastai[2]:
        add.parametric(_riba(S, st, v0, False, hu, hv), u0, u1, gu, 1, 0, gw, RGB)
    if krastai[3]:
        add.parametric(_riba(S, st, v1, False, hu, hv), u0, u1, gu, 0, 1, gw, RGB)


# =============================================================================
#  3 DALIS.  SUKINIAI (spin3D):  S(t) = [spindulys, atstumas ašimi AB]
# =============================================================================

def vazos_R(t):
    """Vazos išorinio kontūro spindulys, t in [0,1] (0 - dugnas, 1 - briauna)."""
    return (1.05
            + 1.15 * math.exp(-((t - 0.30) / 0.30) ** 2)      # vazos pilvas
            - 0.42 * math.exp(-((t - 0.80) / 0.17) ** 2)      # kaklas
            + 0.62 * t ** 7)                                  # atsivėrusi briauna


def vazos_profilis(H=9.0, sien=0.26, dugnas=0.5):
    """Uždara vazos profilio kreivė t in [0,5]:
         [0,1] apatinis dugnas,  [1,2] išorinė sienelė,  [2,3] briauna,
         [3,4] vidinė sienelė,   [4,5] vidinis dugnas."""
    def S(t):
        if t <= 1.0:                                  # dugnas nuo ašies į kraštą
            return [vazos_R(0.0) * t, 0.0]
        if t <= 2.0:                                  # išorė iš apačios į viršų
            return [vazos_R(t - 1.0), H * (t - 1.0)]
        if t <= 3.0:                                  # briauna
            return [vazos_R(1.0) - sien * (t - 2.0), H]
        if t <= 4.0:                                  # vidus iš viršaus į apačią
            u = 4.0 - t
            return [max(0.05, vazos_R(u) - sien), dugnas + (H - dugnas) * u]
        return [max(0.0, (5.0 - t) * (vazos_R(0.0) - sien)), dugnas]
    return S


def taureles_profilis(h0=-0.60, h1=0.10, dr=0.33):
    """Žiedo taurelė - uždaras sukinys (spindulys abiejuose galuose = 0)."""
    def S(t):
        return [dr * math.sin(math.pi * pw(t, 0.9)), h0 + (h1 - h0) * t]
    return S


def toro_profilis(R, r):
    """Toras - apskritimo sukinys (kaspino mazgas)."""
    def S(t):
        return [R + r * math.cos(t), r * math.sin(t)]
    return S


def piltuvo_profilis(r0, r1, h, sien=0.12):
    """Popieriaus piltuvas (buketo vidus) - uždara kreivė t in [0,5]:
         [0,1] apatinis dugnas, [1,2] išorė į viršų, [2,3] briauna,
         [3,4] vidus į apačią,  [4,5] vidinis dugnas."""
    def R(t):
        return r0 + (r1 - r0) * pw(t, 0.75)

    def S(t):
        if t <= 1.0:                                  # dugnas
            return [r0 * pw(t, 0.5), 0.0]             # sqrt - tolygesni žiedai
        if t <= 2.0:                                  # išorė į viršų
            return [R(t - 1.0), h * (t - 1.0)]
        if t <= 3.0:                                  # briauna
            return [R(1.0) - sien * (t - 2.0), h]
        if t <= 4.0:                                  # vidus į apačią
            u = 4.0 - t
            return [R(u) - sien, sien + (h - sien) * u]
        return [(r0 - sien) * pw(5.0 - t, 0.5), sien]  # vidinis dugnas
    return S


# =============================================================================
#  4 DALIS.  PAGALBINĖS FUNKCIJOS
# =============================================================================

def apvalinti(M, k=4):
    """Suapvalina sluoksnio viršūnių koordinates - OFF failas 2-3 kartus
       mažesnis, o formos pokytis nepastebimas."""
    V = []
    for s in M[0]:
        V += [' '.join([str(round(float(x), k)) for x in s.split(' ', 2)])]
    return [V, M[1]]


def padeti_ant(M, y=0.0):
    """Pastumia sluoksnį taip, kad žemiausias jo taškas būtų aukštyje y
       (kad žiedlapiai tikrai lieka ant stalo, o ne jame)."""
    m = min(float(v.split(' ', 2)[1]) for v in M[0])
    return add.move(M, [0.0, y - m, 0.0])


def mastelis(M, s):
    """Sluoksnio M mastelio keitimas nekeičiant taško (0,0,0)
       (add.zoom keičia mastelį modelio centro atžvilgiu - kompensuojame)."""
    c = add.center(M)
    return add.move(add.zoom(M, s), [-c[0] * (1 - s), -c[1] * (1 - s), -c[2] * (1 - s)])


def nukreipk(M, tilt, ang):
    """Į +Y nukreiptą sluoksnį M palenkia kampu tilt kryptimi ang (apie tašką 0)."""
    return add.rotateY(add.rotateX(M, tilt, [0, 0, 0]), math.pi / 2 - ang, [0, 0, 0])


def bezje(P0, P1, P2, P3):
    """Kubinė Bezjė kreivė - stiebo forma."""
    def P(t):
        a, b = (1 - t) ** 3, 3 * (1 - t) ** 2 * t
        c, d = 3 * (1 - t) * t * t, t ** 3
        return [a * P0[i] + b * P1[i] + c * P2[i] + d * P3[i] for i in range(3)]
    return P


def tarp(RGB1, RGB2, s):
    """Spalvų interpoliacija."""
    return [int(RGB1[i] + (RGB2[i] - RGB1[i]) * s) for i in range(3)]


def kryptis(tilt, ang):
    """Vienetinis vektorius (žiedo ašis)."""
    return [math.sin(tilt) * math.cos(ang), math.cos(tilt), math.sin(tilt) * math.sin(ang)]


def t_pagal_auksti(P, y, a=0.0, b=1.0):
    """Suranda kreivės P parametrą t, kuriame kreivė yra aukštyje y
       (dalijimo pusiau metodas)."""
    for i in range(40):                                          # FOR ciklas
        c = (a + b) / 2.0
        if P(c)[1] < y:
            a = c
        else:
            b = c
    return (a + b) / 2.0


# ------------------------------ spalvos --------------------------------------
ZALIA = [46, 125, 50]
ZALIA_T = [27, 82, 36]
RUDA = [96, 60, 36]
STIKLAS = [150, 196, 214]
VANDUO = [104, 166, 192]
POPIERIUS = [244, 232, 208]
POPIERIUS2 = [212, 176, 120]
KASPINAS = [186, 26, 54]

#  rožių spalvų variantai: (centro spalva, krašto spalva)
ROZIU_SPALVOS = [([120, 6, 30], [214, 28, 62]),        # tamsiai raudona
                 ([158, 12, 40], [235, 60, 90]),       # raudona
                 ([190, 60, 100], [246, 150, 180]),    # rožinė
                 ([214, 120, 140], [252, 226, 226])]   # kreminė


# =============================================================================
#  5 DALIS.  MODELIO DALYS (kiekviena grąžina sluoksnį)
# =============================================================================

def rozes_ziedas(spalva_c, spalva_k, grid_u, grid_v, juostos=4,
                 theta_max=THETA_MAX, storis=STORIS):
    """Rožės žiedas - TŪRINIS parametrinis paviršius, dažomas juostomis, kad
       spalva pereitų nuo šviesaus krašto iki tamsaus centro.
       Žiedo ašis - +Y, žiedo pagrindas - taškas (0,0,0)."""
    S = ziedo_pavirsius()

    def st(u, v):                       # žiedlapis plonėja link krašto
        return storis * (1.0 - 0.55 * v)

    for i in range(juostos):                                     # FOR ciklas
        a = THETA_MIN + (theta_max - THETA_MIN) * i / juostos
        b = THETA_MIN + (theta_max - THETA_MIN) * (i + 1) / juostos
        RGB = tarp(spalva_k, spalva_c, i / max(1.0, juostos - 1.0))
        #  kraštai: u pradžia/galas - išorinio ir vidinio žiedlapio galai,
        #  v=0 (žiedo ašis) yra išsigimęs, v=1 - žiedlapio kraštas
        pav_su_storiu(S, a, b, max(3, grid_u // juostos), 0, 1, grid_v,
                      st, RGB, krastai=(i == 0, i == juostos - 1, False, True))
    return add.layer()


def lapas(L, W, grid_u, grid_v, RGB=ZALIA, storis=None, **kw):
    """Vienas TŪRINIS lapas (arba žiedlapis)."""
    if storis is None:
        storis = 0.014 * L

    def st(u, v):                       # lapas plonėja link kraštų
        return storis * (1.0 - 0.45 * abs(v))

    S = lapo_pavirsius(L=L, W=W, **kw)
    #  u=0 ir u=1 yra taškai (išsigimę), v=-1 ir v=1 - lapo kraštai
    pav_su_storiu(S, 0, 1, grid_u, -1, 1, grid_v, st, RGB,
                  krastai=(False, False, True, True))
    return add.layer()


def taurele(grid=26, sepalu=5, ilgis=0.95):
    """Žiedo taurelė: SUKINYS (spin3D) + tūriniai sepalai."""
    add.spin3D([0, -0.60, 0], [0, 0.40, 0], taureles_profilis(),
               0, 1, 16, grid, ZALIA_T)
    dalys = [add.layer()]
    for i in range(sepalu):                                      # FOR ciklas
        s = lapas(ilgis, 0.13, 14, 6, ZALIA, storis=0.02, p=0.55, sag=0.75,
                  fold=0.7, tw=0.0, zub=0.16, dant=7.0)
        s = add.rotateZ(s, -1.05, [0, 0, 0])
        s = add.rotateY(add.move(s, [0, -0.05, 0]), i * TAU / sepalu, [0, 0, 0])
        dalys += [s]
    return add.merge(dalys)


def lapu_grupe(L=2.2, grid_u=22, grid_v=10, lapeliu=3):
    """Sudėtinis rožės lapas: 3 tūriniai lapeliai + lapkotis ir gyslos
       (uždari cilindrai)."""
    add.cylinder([0, 0, 0], [L * 0.75, 0.12 * L, 0], 0.035 * L, 7, ZALIA_T)
    dalys = [add.layer()]
    for i in range(lapeliu):                                     # FOR ciklas
        ilg = L * (0.55 + 0.45 * (i + 1.0) / lapeliu)
        add.mesh(lapas(ilg, 0.30 * ilg, grid_u, grid_v, ZALIA, p=0.72,
                       sag=0.20 * ilg, fold=0.5, tw=0.18, zub=0.11, dant=15.0))
        add.cylinder([0, 0.005 * ilg, 0], [ilg * 0.97, -0.19 * ilg, 0],
                     0.012 * ilg, 5, ZALIA_T)
        lap = add.layer()
        if i < lapeliu - 1:                                      # šoniniai lapeliai
            lap = add.rotateY(lap, (1 - 2 * (i % 2)) * 1.15, [0, 0, 0])
            lap = add.move(lap, [L * 0.42, 0.07 * L, 0])
        else:                                                    # viršutinis lapelis
            lap = add.move(lap, [L * 0.72, 0.12 * L, 0])
        dalys += [lap]
    return add.merge(dalys)


def stiebas(P, grid_t, k, r0, r1, spygliu=0):
    """Stiebas - parametrinė 3D kreivė (Bezjė) su kintančiu spinduliu r(t);
       spygliai - kūgiai."""
    def r(t):
        return r0 + (r1 - r0) * t

    add.curve(P, 0.0, 1.0, grid_t, k, r, ZALIA, False)
    for i in range(spygliu):                                     # FOR ciklas
        t = 0.10 + 0.75 * (i + 0.35 * random.random()) / max(1, spygliu)
        A, B = P(t), P(min(1.0, t + 0.02))
        d = [B[j] - A[j] for j in range(3)]
        nd = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) or 1.0
        d = [d[j] / nd for j in range(3)]
        a = i * 2.4
        s = [math.cos(a), 0.0, math.sin(a)]                      # šoninė kryptis
        pr = s[0] * d[0] + s[1] * d[1] + s[2] * d[2]
        s = [s[j] - pr * d[j] for j in range(3)]
        s[1] -= 0.5                                              # spygliai žemyn
        m = math.sqrt(s[0] ** 2 + s[1] ** 2 + s[2] ** 2) or 1.0
        h = 3.4 * r(t)
        add.cone(A, [A[j] + s[j] / m * h for j in range(3)], 0.8 * r(t), 6, ZALIA_T)
    return add.layer()


# =============================================================================
#  6 DALIS.  MODELIS 1 - 100 ROŽIŲ (dovana mylimajai)
# =============================================================================

def modelis_100_roziu(N=100, detalumas=1.0, failas='100_roziu.off'):
    R_BUK = 8.6              # buketo (kupolo) spindulys
    Y_TOP = 1.6              # kupolo viršus
    KUPOLAS = 3.5            # kupolo aukštis
    Y_MAZGAS = -13.0         # taškas, kuriame susirenka visi stiebai
    POSVYRIS = 0.95          # kraštinių rožių posvyris
    POP_VIRS = -3.2          # popieriaus krašto aukštis

    gu = max(60, int(126 * detalumas))
    gv = max(3, int(4 * detalumas))
    dalys = []

    # --- po vieną rožės tinklą kiekvienai spalvai (naudojami daug kartų) ------
    ROZES = []
    for c, k in ROZIU_SPALVOS:                                   # FOR ciklas
        add.mesh(rozes_ziedas(c, k, gu, gv))
        add.spin3D([0, -0.60, 0], [0, 0.40, 0], taureles_profilis(),
                   0, 1, 10, max(8, int(12 * detalumas)), ZALIA_T)
        ROZES += [add.layer()]
    LAPAS = lapu_grupe(L=3.2, grid_u=max(10, int(18 * detalumas)),
                       grid_v=max(4, int(8 * detalumas)))

    # --- 100 rožių: Fibonačio (aukso kampo) spiralė ant kupolo ----------------
    for i in range(N):                                           # FOR ciklas
        t = (i + 0.5) / N
        rad = R_BUK * math.sqrt(t)
        ang = i * 2.39996322973                                  # aukso kampas
        y = Y_TOP - KUPOLAS * t
        tilt = POSVYRIS * math.sqrt(t)
        p = [rad * math.cos(ang), y, rad * math.sin(ang)]

        M = mastelis(ROZES[i % len(ROZES)], 0.80 + 0.16 * random.random())
        M = add.rotateY(M, TAU * random.random(), [0, 0, 0])     # atsitiktinis posūkis
        dalys += [add.move(nukreipk(M, tilt, ang), p)]

        # --- stiebas: Bezjė kreivė nuo mazgo iki žiedo pagrindo ---------------
        #  (stiebų pradžios šiek tiek išskleistos, kad nesutaptų viena su kita)
        ax = kryptis(tilt, ang)
        kr = 0.20 * math.sqrt(t)
        P = bezje([kr * math.cos(ang), Y_MAZGAS + 0.7 * t, kr * math.sin(ang)],
                  [0.18 * p[0], Y_MAZGAS + 5.0, 0.18 * p[2]],
                  [p[0] - 2.2 * ax[0], p[1] - 2.2 * ax[1], p[2] - 2.2 * ax[2]],
                  [p[0] - 0.35 * ax[0], p[1] - 0.35 * ax[1], p[2] - 0.35 * ax[2]])
        dalys += [stiebas(P, max(8, int(14 * detalumas)), 6, 0.10, 0.075)]

    # --- lapai, iškišti virš popieriaus krašto --------------------------------
    for i in range(20):                                          # FOR ciklas
        a = i * TAU / 20 + 0.2
        L = add.rotateZ(LAPAS, -0.45 - 0.30 * random.random(), [0, 0, 0])
        L = add.rotateY(L, -a, [0, 0, 0])
        dalys += [add.move(L, [9.3 * math.cos(a),
                               POP_VIRS + 0.9 - 0.9 * random.random(),
                               9.3 * math.sin(a)])]

    # --- vyniojamasis popierius: SUKINYS (piltuvas) + 2 tūriniai paviršiai ----
    add.spin3D([0, Y_MAZGAS - 0.4, 0], [0, Y_MAZGAS + 0.6, 0],
               piltuvo_profilis(0.25, 8.4, 10.2), 0, 5,
               max(50, int(120 * detalumas)), max(24, int(60 * detalumas)),
               POPIERIUS2)
    dalys += [add.layer()]

    pav_su_storiu(popieriaus_pavirsius(0.9, 10.9, Y_MAZGAS + 1.4, POP_VIRS,
                                       klosciu=13, gylis=0.10, banga=0.9),
                  0, TAU, max(40, int(120 * detalumas)), 0, 1,
                  max(6, int(16 * detalumas)), 0.09, POPIERIUS,
                  krastai=(False, False, True, True))
    pav_su_storiu(popieriaus_pavirsius(0.75, 9.5, Y_MAZGAS + 1.2, POP_VIRS - 1.3,
                                       klosciu=9, gylis=0.12, banga=0.7),
                  0, TAU, max(40, int(96 * detalumas)), 0, 1,
                  max(6, int(14 * detalumas)), 0.09, POPIERIUS2,
                  krastai=(False, False, True, True))
    dalys += [add.layer()]

    # --- kaspinas: tūrinė juosta + SUKINYS (toras - mazgas) + galai -----------
    Y_KASP = -7.6                # kaspino aukštis
    PLOT = 0.75                  # kaspino pusplotis
    # kaspino spinduliai apskaičiuojami taip, kad juosta liktų virš popieriaus
    RB = popieriaus_r(Y_KASP - PLOT, 0.9, 10.9, Y_MAZGAS + 1.4, POP_VIRS) + 0.10
    RT = popieriaus_r(Y_KASP + PLOT, 0.9, 10.9, Y_MAZGAS + 1.4, POP_VIRS) + 0.10
    R_KASP = (RB + RT) / 2.0

    pav_su_storiu(kaspino_pavirsius(RB, RT, Y_KASP - PLOT, Y_KASP + PLOT, 0.26, 7),
                  0, TAU, max(30, int(96 * detalumas)), 0, 1, 3, 0.07, KASPINAS,
                  krastai=(False, False, True, True))
    dalys += [add.layer()]

    add.spin3D([R_KASP, Y_KASP, 0], [R_KASP, Y_KASP, 1], toro_profilis(0.90, 0.30),
               0, TAU, max(10, int(22 * detalumas)),
               max(10, int(22 * detalumas)), KASPINAS)
    K1 = add.layer()
    dalys += [K1, add.rotateY(add.rotateX(K1, 0.7, [R_KASP, Y_KASP, 0]),
                              0.40, [0, Y_KASP, 0])]

    for s in (1, -1):                                            # FOR ciklas
        G = lapas(5.0, 0.45, max(8, int(22 * detalumas)), 3, KASPINAS,
                  storis=0.07, p=1.0, sag=1.6, fold=0.15, tw=0.0, zub=0.0)
        G = add.rotateZ(G, -1.05, [0, 0, 0])
        dalys += [add.move(add.rotateY(G, s * 0.55, [0, 0, 0]),
                           [R_KASP + 0.1, Y_KASP, 0])]

    add.mesh(apvalinti(add.merge(dalys)))
    add.off(failas)


# =============================================================================
#  7 DALIS.  MODELIS 2 - 3 ROŽĖS VAZOJE
# =============================================================================

def modelis_3_rozes(detalumas=1.0, failas='3_rozes_vazoje.off'):
    H = 9.0                  # vazos aukštis
    SIEN = 0.26              # vazos sienelės storis
    dalys = []

    gu = max(120, int(420 * detalumas))
    gv = max(5, int(12 * detalumas))

    # --- VAZA: SUKINYS iš uždaros profilio kreivės ----------------------------
    add.spin3D([0, 0, 0], [0, 1, 0], vazos_profilis(H, SIEN), 0, 5,
               max(60, int(175 * detalumas)), max(30, int(72 * detalumas)),
               STIKLAS)
    dalys += [add.layer()]

    # --- vanduo vazoje (uždaras cilindras) ------------------------------------
    tv = 0.72
    add.cylinder([0, H * tv - 1.6, 0], [0, H * tv, 0], vazos_R(tv) - SIEN - 0.02,
                 max(24, int(56 * detalumas)), VANDUO)
    dalys += [add.layer()]

    # --- stalviršis (uždaras cilindras) ---------------------------------------
    add.cylinder([0, -0.45, 0], [0, 0.0, 0], 11.0,
                 max(30, int(80 * detalumas)), RUDA)
    dalys += [add.layer()]

    # --- 3 rožės: (kampas, posvyris, žiedo aukštis, mastelis, spalva) ---------
    ROZES = [(0.35, 0.16, 16.2, 1.00, 1),
             (2.55, 0.38, 14.4, 0.90, 0),
             (4.60, 0.30, 15.2, 0.82, 2)]

    for ang, tilt, hgt, s, ci in ROZES:                          # FOR ciklas
        c, k = ROZIU_SPALVOS[ci]
        add.mesh(rozes_ziedas(c, k, gu, gv, juostos=5))
        add.mesh(taurele(grid=max(16, int(30 * detalumas))))
        M = nukreipk(mastelis(add.layer(), 2.05 * s), tilt, ang)

        ax = kryptis(tilt, ang)
        p = [hgt * ax[0], hgt * ax[1], hgt * ax[2]]
        dalys += [add.move(M, p)]

        # --- stiebas: iš vazos kyla vertikaliai, paskui linksta prie žiedo ----
        K = [0.20 * math.cos(ang + 2.0), 0.75, 0.20 * math.sin(ang + 2.0)]
        P = bezje(K,
                  [K[0], H + 7.0, K[2]],
                  [p[0] - 4.0 * ax[0] + 0.9 * math.cos(ang + 1.6),
                   p[1] - 4.0 * ax[1],
                   p[2] - 4.0 * ax[2] + 0.9 * math.sin(ang + 1.6)],
                  [p[0] - 0.55 * ax[0], p[1] - 0.55 * ax[1], p[2] - 0.55 * ax[2]])
        dalys += [stiebas(P, max(20, int(56 * detalumas)),
                          max(6, int(10 * detalumas)), 0.17, 0.13, spygliu=7)]

        # --- lapai ant stiebo (tik virš vazos briaunos) -----------------------
        j = 0
        for yl in (H + 0.9, H + 2.7, H + 4.5):                   # FOR ciklas
            A = P(t_pagal_auksti(P, yl))
            L = lapu_grupe(L=3.0 * s, grid_u=max(12, int(24 * detalumas)),
                           grid_v=max(5, int(10 * detalumas)))
            L = add.rotateZ(L, 0.32 - 0.42 * j, [0, 0, 0])
            L = add.rotateY(L, ang + 2.1 * j + 0.6, [0, 0, 0])
            dalys += [add.move(L, A)]
            j += 1

    # --- nubyrėję žiedlapiai ant stalo ----------------------------------------
    for i in range(6):                                           # FOR ciklas
        c, k = ROZIU_SPALVOS[i % len(ROZIU_SPALVOS)]
        Z = lapas(2.1, 1.05, max(10, int(22 * detalumas)),
                  max(5, int(10 * detalumas)), k, storis=0.05, p=0.62, sag=0.10,
                  fold=0.35, tw=0.08, zub=0.04, dant=5.0)
        a = 0.9 + i * 1.27
        Z = add.rotateZ(Z, 0.12 - 0.25 * (i % 2), [0, 0, 0])
        Z = add.rotateY(Z, 2.0 * a, [0, 0, 0])
        d = 3.4 + 0.9 * i
        Z = padeti_ant(Z, 0.02)                 # ant stalviršio, ne jame
        dalys += [add.move(Z, [d * math.cos(a), 0.0, d * math.sin(a)])]

    add.mesh(apvalinti(add.merge(dalys)))
    add.off(failas)


# =============================================================================
#  8 DALIS.  GENERAVIMAS
# =============================================================================

if __name__ == '__main__':
    print('Generuojami 3D modeliai (OFF formatas):')
    modelis_100_roziu(N=100, detalumas=1.0)
    print('  100_roziu.off')
    modelis_3_rozes(detalumas=1.0)
    print('  3_rozes_vazoje.off')
    print('Baigta.')
