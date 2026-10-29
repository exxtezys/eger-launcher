package com.elium.launcher;

import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.Map;

/** Minecraft Server List Ping: returns "online/max" or throws when the server is down. */
public final class ServerPing {
    private ServerPing() {}

    public record Status(int online, int max) {}

    public static Status ping(String host, int port) throws IOException {
        try (Socket s = new Socket()) {
            s.connect(new InetSocketAddress(host, port), 3000);
            s.setSoTimeout(3000);
            DataOutputStream out = new DataOutputStream(s.getOutputStream());
            DataInputStream in = new DataInputStream(s.getInputStream());

            ByteArrayOutputStream hs = new ByteArrayOutputStream();
            DataOutputStream h = new DataOutputStream(hs);
            h.writeByte(0x00);
            varInt(h, 767); // 1.21.1
            byte[] hb = host.getBytes(StandardCharsets.UTF_8);
            varInt(h, hb.length);
            h.write(hb);
            h.writeShort(port);
            varInt(h, 1);
            varInt(out, hs.size());
            out.write(hs.toByteArray());
            out.writeByte(0x01);
            out.writeByte(0x00);

            readVarInt(in);
            readVarInt(in);
            byte[] json = new byte[readVarInt(in)];
            in.readFully(json);
            Map<String, Object> st = Json.obj(Json.parse(new String(json, StandardCharsets.UTF_8)));
            Map<String, Object> pl = Json.obj(st.get("players"));
            return new Status(((Number) pl.get("online")).intValue(), ((Number) pl.get("max")).intValue());
        }
    }

    private static void varInt(DataOutputStream o, int v) throws IOException {
        while ((v & ~0x7F) != 0) { o.writeByte((v & 0x7F) | 0x80); v >>>= 7; }
        o.writeByte(v);
    }

    private static int readVarInt(DataInputStream in) throws IOException {
        int v = 0, n = 0;
        byte b;
        do {
            b = in.readByte();
            v |= (b & 0x7F) << (7 * n++);
            if (n > 5) throw new IOException("VarInt too big");
        } while ((b & 0x80) != 0);
        return v;
    }
}
