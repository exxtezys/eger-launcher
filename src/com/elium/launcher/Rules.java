package com.elium.launcher;

import java.util.List;
import java.util.Map;

/** Mojang library/argument "rules" evaluation for Windows; all features are treated as disabled. */
final class Rules {
    private Rules() {}

    static boolean allowed(Object rulesObj) {
        List<Object> rules = Json.arr(rulesObj);
        if (rules.isEmpty()) return true;
        boolean allow = false;
        for (Object o : rules) {
            Map<String, Object> r = Json.obj(o);
            if (matches(r)) allow = "allow".equals(Json.str(r, "action"));
        }
        return allow;
    }

    private static boolean matches(Map<String, Object> r) {
        if (r.get("features") != null) return false;
        Map<String, Object> os = Json.obj(r.get("os"));
        if (os == null) return true;
        String name = Json.str(os, "name");
        if (name != null && !name.equals("windows")) return false;
        String arch = Json.str(os, "arch");
        if (arch != null && arch.equals("x86") && System.getProperty("os.arch").contains("64")) return false;
        return true;
    }
}
