# -*- coding: utf-8 -*-
"""반각 고유 이름 영문표(AWW 표기 우선, 없는 것은 아래 표). → work/text/romaji.tsv.  9칸 이하 검사."""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
AW = 'C:/claude/project/aww-kr-patch/'
T = """
858 T1 Chihe|859 T1 HoniⅠ|860 T1 HoniⅡ|861 G4M|863 H8K|866 T3 Chinu|868 T4 Chito|869 T4 Horo|870 5.5in.Gun|871 T5 Chiri|872 Ki100|878 88㎜AAG
879 T89 Igo|881 T94 TK|882 T95 Ha-Go|883 B5N|884 T97 Kai|885 T97 Chiha|886 Ki27|887 T97 TE|888 Ki21|889 T98 Ke-Ni|890 D3A1|891 D3A2|892 G.Zeppeln
893 HBB|897 PoWales|899 Iowa|900 Akagi|904 Unryu|905 Essex|906 EbenEmael|912 Marines|913 Kaga|915 MechInf|917 Kikka|919 P1Y|924 CromwelⅥⅧ
925 Gneisenau|933 VolksGren|934 Guards|936 Kongo|938 Proto O-I|939 ProtoSoki|940 N1K2|941 Civilian|949 ShermnJmb|950 J8M|951 Shokaku|952 Ki44
953 SmallHQ|955 J7W|956 J7W Kai|958 Motorized|959 MotInf|962 D4Y|968 Spit.ⅩⅪ|969 Spit.ⅫⅣ|970 SpitfireⅠ|971 Zuikaku|976 Soryu|981 Taiho
982 Large HQ|984 Dummy|988 ChurchlⅥⅧ|990 Mid HQ|993 Tiger（P）|995 TetrrchCS|997 B6N|1002 Ka-Mi|1003 Nagato|1004 Nashorn|1006 Ki84|1007 Ki43-I
1008 Ki43-II|1009 Ki43-III|1015 Humber Ⅲ|1018 ValentⅫⅠ|1022 Ki61|1023 Hiryu|1026 Vickers|1028 FokkrDⅫⅫⅠ|1029 Fugaku|1033 Priest|1040 Inf 41
1041 Inf 44|1045 Potez631|1047 Maginot|1053 Musashi|1054 Mutsu|1057 Yamato|1058 JagdTiger|1059 JagdPanth|1066 J2M|1067 Paratroop|1071 B7A
1074 A6M2|1075 A6M3-22|1076 A6M3-32|1077 A6M5|1079 RedDevils|1080 A7M|1081 Repulse|1082 Radar
1880 Airborne|1881 UK BEF|1882 Fr-1AGr|1883 Fr-2AGr|1884 Maginot|1885 2nd AF|1886 3rd AF|1887 UK SE A|1888 UK SW A|1889 Gre-1A|1890 Gre-2A
1891 BrestFort|1892 Timoshnko|1893 West FtA|1894 BryanskFA|1895 OuterDef|1896 VoroneFtA|1897 Kempf A|1898 It Fleet|1899 CenterFtA|1900 SteppeFtA
1901 UK-21AGr|1903 US-9A|1904 Can-1A|1905 VistulAGr|1906 CenterAGr|1907 Belo2FtA|1908 Belo1FtA|1909 Ukr1FtA|1910 PersiaAGr|1911 S.IndiaHA
1912 1st Flt|1913 E.IndiaHA|1914 3rd Flt|1915 Ind-1Cp|1916 OutMongol|1917 Manchuria|1918 Soviet|1919 1AirFlt|1920 2AirFlt|1921 5AirFlt|1922 2SubFlt
1923 Ind-11thD|1924 Ind-9thD|1925 UK Z Flt|1926 Paratroop|1927 West Flt|1928 East Flt|1929 ABDA Flt|1930 MO Inv|1931 MO Strike|1932 US TF17
1933 US TF11|1934 2ndStrike|1935 1stStrike|1936 1stFleet|1937 MI Sup|1938 US TF16|1939 US TF86|1940 Reinforce|1941 2nd Flt|1942 US TF18|1943 Kuma Det
1944 Aoba Det|1945 Maizuru|1946 1stMarine|1947 5thMarine|1948 India HA|1949 Ind-5thCp|1950 East AGr|1951 Calif HA|1952 Wash HA|1953 US TG86|1954 Utah HA
1955 Ind-17D|1956 Ind-23D|1957 Ind-20D|1958 Ind-49Bri|1959 AssamReg|1960 11AirFlt|1961 US TF58|1962 KonForce|1963 1stRaid|1964 2ndRaid|1965 7th Flt
1966 US TF51|1967 Navy|1968 US TF50|1969 FarEastHA|1970 S.IndFtA|1971 E.IndFtA|1972 Ind-1stCp|1973 PersiaAGr|1974 Maizuru|1975 3rd Flt8
1980 Le Havre|1982 Exeter|1984 Norwich|1987 Tirana|1988 Taranto|1989 LimnosIs.|1990 Salonika|1991 Lamia|1992 OlympusMt|1993 Patras|1994 Ioannina
1995 Skopje|1996 Grodno|1997 Kobrin|1998 Bereza|1999 Slonim|2000 Pinsk|2001 Vitebsk|2002 Kopys|2003 Shklov|2004 Gorki|2005 Chausy|2006 Kuzino
2007 Krasny|2008 Mstislavl|2009 Chislavch|2010 Pochinok|2011 Dorogobuz|2012 Novgorod|2013 Chernigov|2015 Borispol|2016 Kanev|2017 Bakhmach
2018 Priluki|2019 Konotop|2021 Lubny|2023 Rzhev|2024 Klin|2025 Borodino|2026 Kaluga|2027 Serpukhov|2028 Noginsk|2029 Kolomna|2030 Mikhailov
2033 Balashov|2035 Rossosh|2036 Boguchar|2037 Millerovo|2038 Voroshlvg|2039 KalachDon|2041 GumrakAir|2042 Gorodishc|2043 Aleksndrv|2044 Yelshanka
2045 Central|2046 MamayevKg|2047 RedOct Fc|2048 BarrikdFc|2049 TractorFc|2050 Rynok|2051 Krasnogrd|2052 Poltava|2053 Chuguyev|2054 NVodolaga
2055 Krasnopol|2056 Grayvoron|2057 Akhtyrka|2058 Lebedin|2059 Kotelva|2060 St.Johns|2061 Augusta|2062 Charlttwn|2063 GlaceBay|2064 Belopolye
2065 Rylsk|2066 Navlya|2067 Kromy|2068 Prokhorvk|2069 Oboyan|2070 Lgov|2071 Fatezh|2072 Livny|2073 St.Oskol|2074 Le Havre|2075 VillersBc|2076 Conde
2077 Vire|2078 Valognes|2079 Coutances|2080 Granville|2082 Amsterdam|2083 Lyon|2084 Huy|2085 Malmedy|2086 St.Vith|2088 Eindhoven|2091 Prague
2092 Nurnberg|2094 Breslau|2095 Hannover|2096 Jaipur|2097 Colombo|2098 Bangalore|2099 Patna|2100 Kanpur|2101 Bhopal|2102 Nagpur|2103 Hyderabad
2104 Nomonhan|2105 Bal Hill|2106 Kui Hill|2107 Hill 733|2108 Hill 739|2109 Hui Hill|2110 Haradai|2111 Hill 372|2112 Hill 737|2113 Hill 731
2114 Hill 755|2115 Hill 749|2116 Wheeler|2117 Ewa|2118 Kaneohe|2119 KotaBharu|2120 Kroh|2121 Trengganu|2122 K.Lipis|2123 Malacca|2124 Kluang
2125 Johor|2126 Sampit|2127 Banjarmsn|2128 Tanjungkr|2129 Semarang|2130 Surakarta|2131 Surabaya|2132 Buin|2133 Tulagi|2134 Buna|2135 Guam|2136 Wake
2137 Midway|2138 Johnston|2139 Attu|2140 Kiska|2141 DutchHbr|2142 Kodiak|2143 Buka|2144 Munda|2145 Tenaru|2146 LungaFld|2147 2nd Field|2148 Kukum
2149 AustenMt.|2150 Rangoon|2151 Akyab|2152 Masulipat|2153 Vizagapat|2154 Madurai|2155 Calcutta|2156 Chittagng|2157 SanDiego|2158 Sacrament|2159 Boise
2160 Portland|2161 Spokane|2162 Vancouver|2163 Phoenix|2164 LasVegas|2165 Denver|2166 Regina|2167 Kalewa|2168 Homalin|2169 Mawlaik|2170 Taungdaw
2171 Kalemyo|2172 Tonzang|2173 Hentam|2174 Maungkan|2175 Silchar|2176 Milne|2177 Talasea|2178 Gasmata|2179 Sag Sag|2180 Bogia|2181 Wewak|2182 Guimaras
2183 Palau|2184 Brunei|2185 Cagayan|2186 Surigao|2187 Tacloban|2188 Legazpi|2189 Naga|2190 Kure|2191 Matsuyama|2192 Tokuyama|2193 Shimonsek|2194 Oita
2195 Fukuoka|2196 Miyazaki|2197 Sasebo|2198 Nagasaki|2199 Kagoshima|2200 Machinato|2201 Kadena|2202 Hagushi|2203 Tanabaru|2204 Yomitan|2205 Ishikawa
2206 Gushikawa|2207 Yonabaru|2208 Itoman|2209 Makabe|2210 Minatogwa|2211 Toyama|2212 Toyohashi|2213 Shizuoka|2214 Maebashi|2215 Utsunomya|2216 Sendai
2217 Hitachi|2218 Mito|2219 VoronFta|2220 KurskFta|2221 CityDef|2222 West Line|2223 26A Line|2224 Novgorod|2225 9A Line|2226 City L1|2227 City L2
2228 5A Line|2229 66A Line|2230 57A Line|2232 Ger-4A|2233 KurskBASE|2234 SteppeLn|2235 Gachev|2236 Ger-5A
"""
M = {}
for x in T.replace('\n', '|').split('|'):
    x = x.strip()
    if x:
        n, v = x.split(' ', 1); M['%05d' % int(n)] = v
A = {}
for l in open(AW + 'work/smalltext/smalltext.tsv', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 8 and p[1] in ('units', 'places', 'names', 'terrain') and p[7]: A.setdefault(p[4].rstrip(), p[7].rstrip())
rows = []
for f, g in (('work/text/small.tsv', 'N'), ('work/text/small3.tsv', 'D')):
    for l in open(f, encoding='utf-8'):
        if l[0] != '#':
            p = l.rstrip('\n').split('\t')
            if p[1] == g and not (g == 'D' and int(p[0]) < 1880): rows.append((p[0], p[4]))
out = []; miss = []; over = []; han = []
for i, j in rows:
    v = M.get(i) or A.get(j)
    if not v: miss.append((i, j)); continue
    if len(v) > 9: over.append((i, v))
    if re.search('[가-힣]', v): han.append(v)
    out.append('%s\t%s\t%s\n' % (i, j, v))
print(len(rows), len(out), '없음', miss[:20], '9칸 넘침', over, '한글 낀 표기', han)
open('work/text/romaji.tsv', 'w', encoding='utf-8', newline='\n').write(''.join(out))
