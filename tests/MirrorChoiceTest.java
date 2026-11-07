package test;

import com.elium.launcher.Mirrors;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;

/**
 * Выбор зеркала переживает перезапуск: разведка один раз, дальше берём сохранённый выбор.
 */
public class MirrorChoiceTest {
    private static int failed = 0;

    static void eq(String what, Object expected, Object actual) {
        if (!Objects.equals(expected, actual)) {
            System.out.println("FAIL " + what + ": ожидалось " + expected + ", получено " + actual);
            failed++;
        }
    }

    private static final String ORIGINAL = "https://libraries.minecraft.net/a.jar";
    private static final String MIRROR = "https://bmclapi2.bangbang93.com/libraries/a.jar";

    public static void main(String[] args) throws Exception {
        Path tmp = Files.createTempDirectory("eger-choice");
        Path file = tmp.resolve("mirror-choice.properties");
        try {
            // 1. Разведка выбрала зеркало — выбор лёг в файл.
            Mirrors.setStore(file);
            Mirrors.resetChoices();
            Mirrors.prefer("libraries", 1);
            eq("файл создан", true, Files.exists(file));
            String body = Files.readString(file, StandardCharsets.UTF_8);
            eq("в файле libraries=1", true, body.contains("libraries=1"));

            // 2. Новый запуск: выбор читается и задаёт порядок источников.
            Mirrors.resetChoices();
            eq("до загрузки оригинал первым", List.of(ORIGINAL, MIRROR), Mirrors.ordered(ORIGINAL));
            Mirrors.loadStore();
            eq("после загрузки зеркало первым", List.of(MIRROR, ORIGINAL), Mirrors.ordered(ORIGINAL));

            // 3. Разведка сказала «оригинал работает» — выбор снимается, зеркало больше не первое.
            Mirrors.prefer("libraries", 0);
            eq("после prefer(0) оригинал первым", List.of(ORIGINAL, MIRROR), Mirrors.ordered(ORIGINAL));
            eq("ключ убран из файла", false,
                    Files.readString(file, StandardCharsets.UTF_8).contains("libraries="));

            // 4. Мусор в файле не ломает запуск: неизвестная группа и кривой индекс игнорируются.
            Files.writeString(file, "libraries=99\nnohost=1\nassets=abc\n", StandardCharsets.UTF_8);
            Mirrors.resetChoices();
            Mirrors.loadStore();
            eq("кривой индекс игнорируется", List.of(ORIGINAL, MIRROR), Mirrors.ordered(ORIGINAL));
            eq("assets не сломан", List.of(
                            "https://resources.download.minecraft.net/ab/cdef",
                            "https://bmclapi2.bangbang93.com/assets/ab/cdef"),
                    Mirrors.ordered("https://resources.download.minecraft.net/ab/cdef"));

            // 5. Файла нет — тихо стартуем с оригинала.
            Mirrors.resetChoices();
            Mirrors.setStore(tmp.resolve("нет-такого.properties"));
            Mirrors.loadStore();
            eq("нет файла — оригинал первым", List.of(ORIGINAL, MIRROR), Mirrors.ordered(ORIGINAL));

            // 6. Приём несохранённого выбора не должен создавать файл.
            Mirrors.resetChoices();
            eq("reset снимает выбор", List.of(ORIGINAL, MIRROR), Mirrors.ordered(ORIGINAL));
        } finally {
            Mirrors.setStore(null);
            Mirrors.resetChoices();
            Files.walk(tmp).sorted(java.util.Comparator.reverseOrder()).forEach(p -> {
                try { Files.deleteIfExists(p); } catch (java.io.IOException ignored) {}
            });
        }

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
        System.exit(0);
    }
}
