package test;

import com.elium.launcher.JavaRuntime;
import java.util.List;
import java.util.Objects;

public class JavaUrlTest {
    private static int failed = 0;

    static void eq(String what, Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            System.out.println("FAIL " + what + ":\n  ожидалось " + expected + "\n  получено  " + actual);
            failed++;
        }
    }

    public static void main(String[] args) {
        eq("windows x64", List.of(
                        "https://mirrors.tuna.tsinghua.edu.cn/Adoptium/21/jre/x64/windows/OpenJDK21U-jre_x64_windows_hotspot_21.0.13_9.zip",
                        "https://gh-proxy.com/https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jre_x64_windows_hotspot_21.0.13_9.zip"),
                JavaRuntime.mirrorUrls("21.0.13+9", "windows", "x64"));

        eq("linux — tar.gz, распаковки нет — без зеркал", List.of(), JavaRuntime.mirrorUrls("21.0.13+9", "linux", "x64"));
        eq("пустая версия — без зеркал", List.of(), JavaRuntime.mirrorUrls("", "windows", "x64"));
        eq("мусор в версии — без зеркал", List.of(), JavaRuntime.mirrorUrls("latest", "windows", "x64"));

        // C1: константа sha1 пинованного zip должна присутствовать и быть верного формата
        String zipSha1 = JavaRuntime.MIRROR_ZIP_SHA1;
        eq("MIRROR_ZIP_SHA1 не пусто", true, zipSha1 != null && zipSha1.length() == 40);
        eq("MIRROR_ZIP_SHA1 hex", true, zipSha1 != null && zipSha1.matches("[0-9a-f]{40}"));
        eq("MIRROR_ZIP_SIZE > 0", true, JavaRuntime.MIRROR_ZIP_SIZE > 0);

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
    }
}
