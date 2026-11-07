package test;

import com.elium.launcher.Mirrors;
import java.util.List;
import java.util.Objects;

public class MirrorsTest {
    private static int failed = 0;

    static void eq(String what, Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            System.out.println("FAIL " + what + ": ожидалось " + expected + ", получено " + actual);
            failed++;
        }
    }

    public static void main(String[] args) {
        eq("manifest", List.of("https://bmclapi2.bangbang93.com/mc/game/version_manifest_v2.json"),
                Mirrors.alternatives("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"));

        eq("piston-data", List.of("https://bmclapi2.bangbang93.com/v1/objects/30c7/client.jar"),
                Mirrors.alternatives("https://piston-data.mojang.com/v1/objects/30c7/client.jar"));

        eq("neo maven", List.of(
                        "https://bmclapi2.bangbang93.com/maven/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar",
                        "https://maven.creeperhost.net/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar"),
                Mirrors.alternatives("https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.252/neoforge-21.1.252-installer.jar"));

        eq("libraries", List.of("https://bmclapi2.bangbang93.com/libraries/com/mojang/logging/1.5.10/logging-1.5.10.jar"),
                Mirrors.alternatives("https://libraries.minecraft.net/com/mojang/logging/1.5.10/logging-1.5.10.jar"));

        eq("assets", List.of("https://bmclapi2.bangbang93.com/assets/ab/cdef"),
                Mirrors.alternatives("https://resources.download.minecraft.net/ab/cdef"));

        eq("github api", List.of("https://gh-proxy.com/https://api.github.com/repos/a/b/releases/latest"),
                Mirrors.alternatives("https://api.github.com/repos/a/b/releases/latest"));

        eq("github release", List.of("https://gh-proxy.com/https://github.com/a/b/releases/download/v1/x.jar"),
                Mirrors.alternatives("https://github.com/a/b/releases/download/v1/x.jar"));

        eq("неизвестный", List.of(), Mirrors.alternatives("https://example.com/x"));

        eq("ordered: оригинал первым",
                List.of("https://libraries.minecraft.net/a.jar", "https://bmclapi2.bangbang93.com/libraries/a.jar"),
                Mirrors.ordered("https://libraries.minecraft.net/a.jar"));

        eq("ordered: неизвестный", List.of("https://example.com/x"), Mirrors.ordered("https://example.com/x"));

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
    }
}
