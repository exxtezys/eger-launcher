package com.elium.launcher;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Minimal JSON parser/writer: objects -> Map, arrays -> List, numbers -> Double. */
public final class Json {
    private final String s;
    private int i;

    private Json(String s) { this.s = s; }

    public static Object parse(String text) {
        Json p = new Json(text);
        p.ws();
        Object v = p.value();
        p.ws();
        if (p.i != p.s.length()) throw p.err("trailing data");
        return v;
    }

    @SuppressWarnings("unchecked")
    public static Map<String, Object> obj(Object o) { return (Map<String, Object>) o; }

    @SuppressWarnings("unchecked")
    public static List<Object> arr(Object o) { return o == null ? List.of() : (List<Object>) o; }

    public static String str(Map<String, Object> m, String k) {
        Object v = m.get(k);
        return v == null ? null : v.toString();
    }

    private RuntimeException err(String msg) { return new IllegalArgumentException("JSON: " + msg + " at " + i); }

    private void ws() { while (i < s.length() && Character.isWhitespace(s.charAt(i))) i++; }

    private Object value() {
        if (i >= s.length()) throw err("unexpected end");
        char c = s.charAt(i);
        switch (c) {
            case '{': return object();
            case '[': return array();
            case '"': return string();
            case 't': expect("true"); return Boolean.TRUE;
            case 'f': expect("false"); return Boolean.FALSE;
            case 'n': expect("null"); return null;
            default: return number();
        }
    }

    private void expect(String word) {
        if (!s.startsWith(word, i)) throw err("expected " + word);
        i += word.length();
    }

    private Map<String, Object> object() {
        Map<String, Object> m = new LinkedHashMap<>();
        i++; ws();
        if (s.charAt(i) == '}') { i++; return m; }
        while (true) {
            ws();
            String k = string();
            ws();
            if (s.charAt(i++) != ':') throw err("expected :");
            ws();
            m.put(k, value());
            ws();
            char c = s.charAt(i++);
            if (c == '}') return m;
            if (c != ',') throw err("expected , or }");
        }
    }

    private List<Object> array() {
        List<Object> l = new ArrayList<>();
        i++; ws();
        if (s.charAt(i) == ']') { i++; return l; }
        while (true) {
            ws();
            l.add(value());
            ws();
            char c = s.charAt(i++);
            if (c == ']') return l;
            if (c != ',') throw err("expected , or ]");
        }
    }

    private String string() {
        if (s.charAt(i) != '"') throw err("expected string");
        i++;
        StringBuilder b = new StringBuilder();
        while (true) {
            char c = s.charAt(i++);
            if (c == '"') return b.toString();
            if (c != '\\') { b.append(c); continue; }
            char e = s.charAt(i++);
            switch (e) {
                case 'n': b.append('\n'); break;
                case 't': b.append('\t'); break;
                case 'r': b.append('\r'); break;
                case 'b': b.append('\b'); break;
                case 'f': b.append('\f'); break;
                case 'u': b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                default: b.append(e);
            }
        }
    }

    private Double number() {
        int st = i;
        while (i < s.length() && "+-0123456789.eE".indexOf(s.charAt(i)) >= 0) i++;
        if (st == i) throw err("unexpected char '" + s.charAt(i) + "'");
        return Double.parseDouble(s.substring(st, i));
    }

    public static String write(Object o) {
        StringBuilder b = new StringBuilder();
        write(o, b, 0);
        return b.toString();
    }

    private static void write(Object o, StringBuilder b, int ind) {
        if (o == null) b.append("null");
        else if (o instanceof String str) quote(str, b);
        else if (o instanceof Number n) {
            double d = n.doubleValue();
            if (d == Math.rint(d) && Math.abs(d) < 1e15) b.append((long) d); else b.append(d);
        } else if (o instanceof Boolean) b.append(o);
        else if (o instanceof Map<?, ?> m) {
            b.append("{");
            boolean first = true;
            for (Map.Entry<?, ?> e : m.entrySet()) {
                b.append(first ? "\n" : ",\n").append("  ".repeat(ind + 1));
                first = false;
                quote(e.getKey().toString(), b);
                b.append(": ");
                write(e.getValue(), b, ind + 1);
            }
            if (!first) b.append("\n").append("  ".repeat(ind));
            b.append("}");
        } else if (o instanceof List<?> l) {
            b.append("[");
            for (int k = 0; k < l.size(); k++) {
                b.append(k == 0 ? "\n" : ",\n").append("  ".repeat(ind + 1));
                write(l.get(k), b, ind + 1);
            }
            if (!l.isEmpty()) b.append("\n").append("  ".repeat(ind));
            b.append("]");
        } else quote(o.toString(), b);
    }

    private static void quote(String str, StringBuilder b) {
        b.append('"');
        for (char c : str.toCharArray()) {
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default:
                    if (c < 0x20) b.append(String.format("\\u%04x", (int) c)); else b.append(c);
            }
        }
        b.append('"');
    }
}
