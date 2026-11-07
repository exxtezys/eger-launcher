package com.elium.launcher;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.nio.file.Path;

/**
 * Р—РµСЂРєР°Р»Р° РґР»СЏ Р·Р°РіСЂСѓР·РѕРє: Р°РґСЂРµСЃР°, РєСѓРґР° РїРµСЂРµРµС…Р°С‚СЊ, РµСЃР»Рё РѕС„РёС†РёР°Р»СЊРЅС‹Р№ С…РѕСЃС‚ РЅРµ РѕС‚РІРµС‡Р°РµС‚.
 * Р’СЃРµ Р°РґСЂРµСЃР° Р·РґРµСЃСЊ РїСЂРѕРІРµСЂРµРЅС‹ РІСЂСѓС‡РЅСѓСЋ; РІС‹РґСѓРјС‹РІР°С‚СЊ РЅРѕРІС‹Рµ РЅРµР»СЊР·СЏ.
 */
public final class Mirrors {
    /** Р“СЂСѓРїРїР° С…РѕСЃС‚РѕРІ: Сѓ РєР°Р¶РґРѕР№ СЃРІРѕР№ РЅР°Р±РѕСЂ РєР°РЅРґРёРґР°С‚РѕРІ Рё СЃРІРѕР№ СЂРµР·СѓР»СЊС‚Р°С‚ СЂР°Р·РІРµРґРєРё. */
    static final class Group {
        final String name;
        final String originalProbe;
        final List<String> mirrorProbes;
        final List<Rule> rules;

        Group(String name, String originalProbe, List<String> mirrorProbes, List<Rule> rules) {
            this.name = name;
            this.originalProbe = originalProbe;
            this.mirrorProbes = mirrorProbes;
            this.rules = rules;
        }
    }

    /** РџСЂР°РІРёР»Рѕ РїРѕРґСЃС‚Р°РЅРѕРІРєРё: РїСЂРµС„РёРєСЃ РѕС„РёС†РёР°Р»СЊРЅРѕРіРѕ Р°РґСЂРµСЃР° -> РїСЂРµС„РёРєСЃ Р·РµСЂРєР°Р»Р°. */
    static final class Rule {
        final String from;
        final String to;

        Rule(String from, String to) {
            this.from = from;
            this.to = to;
        }

        String apply(String url) {
            return url.startsWith(from) ? to + url.substring(from.length()) : null;
        }
    }

    private static final String BMCL = "https://bmclapi2.bangbang93.com/";
    private static final String GH_PROXY = "https://gh-proxy.com/";
    private static final String CREEPERHOST = "https://maven.creeperhost.net/";

    private static final List<Group> GROUPS = List.of(
            new Group("piston",
                    "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json",
                    List.of(BMCL + "mc/game/version_manifest_v2.json"),
                    List.of(new Rule("https://piston-meta.mojang.com/", BMCL),
                            new Rule("https://piston-data.mojang.com/", BMCL))),

            new Group("libraries",
                    "https://libraries.minecraft.net/com/mojang/logging/1.5.10/logging-1.5.10.jar",
                    List.of(BMCL + "libraries/com/mojang/logging/1.5.10/logging-1.5.10.jar"),
                    List.of(new Rule("https://libraries.minecraft.net/", BMCL + "libraries/"))),

            new Group("assets",
                    "https://resources.download.minecraft.net/b6/b62ca8ec10d07e6bf5ac8dae0c8c1d2e6a1e3356",
                    List.of(BMCL + "assets/b6/b62ca8ec10d07e6bf5ac8dae0c8c1d2e6a1e3356"),
                    List.of(new Rule("https://resources.download.minecraft.net/", BMCL + "assets/"))),

            new Group("neomaven",
                    "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml",
                    List.of(BMCL + "maven/net/neoforged/neoforge/maven-metadata.xml",
                            CREEPERHOST + "net/neoforged/neoforge/maven-metadata.xml"),
                    List.of(new Rule("https://maven.neoforged.net/releases/", BMCL + "maven/"),
                            new Rule("https://maven.neoforged.net/releases/", CREEPERHOST))),

            new Group("github",
                    "https://api.github.com/repos/exxtezys/eger-launcher/releases/latest",
                    List.of(GH_PROXY + "https://api.github.com/repos/exxtezys/eger-launcher/releases/latest"),
                    List.of(new Rule("https://api.github.com/", GH_PROXY + "https://api.github.com/"),
                            new Rule("https://github.com/", GH_PROXY + "https://github.com/"))));

    /** РџСЂРµРґРїРѕС‡С‚РµРЅРёРµ РїРѕ РіСЂСѓРїРїР°Рј: 0 вЂ” РѕС„РёС†РёР°Р»СЊРЅС‹Р№ С…РѕСЃС‚, 1..n вЂ” РЅРѕРјРµСЂ Р·РµСЂРєР°Р»Р°. */
    private static final Map<String, Integer> preferred = new java.util.concurrent.ConcurrentHashMap<>();

    /** Куда складывать выбор разведки, чтобы не искать заново при каждом запуске. */
    private static volatile Path store;

    private Mirrors() {}

    /** Задать файл для сохранения выбора (null — не сохранять; тесты). */
    public static void setStore(Path file) {
        store = file;
    }

    /** Забыть выбор в памяти (файл не трогаем). */
    public static void resetChoices() {
        preferred.clear();
    }

    /** Прочитать сохранённый выбор с прошлого запуска. Нет файла или мусор — молча стартуем с оригинала. */
    public static void loadStore() {
        Path f = store;
        if (f == null || !java.nio.file.Files.exists(f)) return;
        java.util.Properties p = new java.util.Properties();
        try (java.io.Reader r = java.nio.file.Files.newBufferedReader(f, java.nio.charset.StandardCharsets.UTF_8)) {
            p.load(r);
        } catch (java.io.IOException e) {
            System.err.println("выбор зеркала не прочитан: " + e.getMessage());
            return;
        }
        Map<String, Integer> choices = new LinkedHashMap<>();
        for (String name : p.stringPropertyNames()) {
            try {
                choices.put(name, Integer.parseInt(p.getProperty(name).trim()));
            } catch (NumberFormatException ignored) {
                // мусор в файле — просто пропускаем
            }
        }
        importChoices(choices);
    }

    private static void saveStore() {
        Path f = store;
        if (f == null) return;
        StringBuilder b = new StringBuilder();
        for (Group g : GROUPS) {
            Integer v = preferred.get(g.name);
            if (v != null && v > 0) b.append(g.name).append('=').append(v).append('\n');
        }
        try {
            if (b.length() == 0) {
                java.nio.file.Files.writeString(f, "", java.nio.charset.StandardCharsets.UTF_8);
                return;
            }
            java.nio.file.Files.createDirectories(f.toAbsolutePath().getParent());
            java.nio.file.Files.writeString(f, b.toString(), java.nio.charset.StandardCharsets.UTF_8);
        } catch (java.io.IOException e) {
            System.err.println("выбор зеркала не сохранён: " + e.getMessage());
        }
    }

    static List<Group> groups() {
        return GROUPS;
    }

    static Integer preferred(String group) {
        return preferred.get(group);
    }

    /** Выбор разведки: 0 — оригинал, 1..n — номер зеркала. Сразу сохраняется на диск. */
    public static void prefer(String group, int mirrorIndex) {
        if (mirrorIndex <= 0) preferred.remove(group);
        else preferred.put(group, mirrorIndex);
        saveStore();
    }

    private static Group groupOf(String url) {
        for (Group g : GROUPS) {
            for (Rule r : g.rules) if (url.startsWith(r.from)) return g;
        }
        return null;
    }

    /** Имя группы хостов для адреса (null — адрес без зеркал). */
    static String groupName(String url) {
        Group g = groupOf(url);
        return g == null ? null : g.name;
    }

    static Group group(String name) {
        for (Group g : GROUPS) if (g.name.equals(name)) return g;
        return null;
    }

    /** РљР°РЅРґРёРґР°С‚С‹-Р·РµСЂРєР°Р»Р° РґР»СЏ РѕС„РёС†РёР°Р»СЊРЅРѕРіРѕ Р°РґСЂРµСЃР°, РїРѕ РїРѕСЂСЏРґРєСѓ, Р±РµР· СЃР°РјРѕРіРѕ РѕСЂРёРіРёРЅР°Р»Р°. */
    public static List<String> alternatives(String url) {
        Group g = groupOf(url);
        if (g == null) return List.of();
        List<String> out = new ArrayList<>();
        for (Rule r : g.rules) {
            String m = r.apply(url);
            if (m != null && !out.contains(m)) out.add(m);
        }
        return out;
    }

    /**
     * РџРѕР»РЅС‹Р№ РїРѕСЂСЏРґРѕРє РёСЃС‚РѕС‡РЅРёРєРѕРІ РґР»СЏ Р°РґСЂРµСЃР°: РѕС„РёС†РёР°Р»СЊРЅС‹Р№ РїРµСЂРІС‹Рј, РµСЃР»Рё СЂР°Р·РІРµРґРєР°
     * РЅРµ РїРѕРєР°Р·Р°Р»Р°, С‡С‚Рѕ РѕРЅ РЅРµРґРѕСЃС‚СѓРїРµРЅ, РёРЅР°С‡Рµ РїРµСЂРІС‹Рј РёРґС‘С‚ СЂР°Р±РѕС‡РµРµ Р·РµСЂРєР°Р»Рѕ.
     */
    public static List<String> ordered(String url) {
        List<String> mirrors = alternatives(url);
        List<String> out = new ArrayList<>();
        Group g = groupOf(url);
        Integer pref = g == null ? null : preferred.get(g.name);
        if (pref != null && pref >= 1 && pref <= mirrors.size()) {
            out.add(mirrors.get(pref - 1));
            out.add(url);
            for (String m : mirrors) if (!out.contains(m)) out.add(m);
        } else {
            out.add(url);
            out.addAll(mirrors);
        }
        return out;
    }

    /** РЎРѕС…СЂР°РЅС‘РЅРЅС‹Р№ РІС‹Р±РѕСЂ СЂР°Р·РІРµРґРєРё: "group=index" РїРѕ СЃС‚СЂРѕРєРµ РЅР° РіСЂСѓРїРїСѓ. */
    static Map<String, Integer> exportChoices() {
        return new LinkedHashMap<>(preferred);
    }

    static void importChoices(Map<String, Integer> choices) {
        for (Group g : GROUPS) {
            Integer v = choices.get(g.name);
            if (v != null && v >= 0 && v <= g.mirrorProbes.size()) {
                if (v == 0) preferred.remove(g.name);
                else preferred.put(g.name, v);
            }
        }
    }
}
