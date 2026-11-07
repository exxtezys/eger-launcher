package test;

import com.elium.launcher.LauncherApp;
import com.elium.launcher.Net;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** Текст, который видит игрок, когда не ответил ни один источник. */
public class ErrorTextTest {
    private static int failed = 0;

    static void check(String what, boolean ok) {
        if (!ok) { System.out.println("FAIL " + what); failed++; }
    }

    public static void main(String[] args) throws Exception {
        Net.resetHostOverrides();
        Path dir = Files.createTempDirectory("errtext");
        IOException err = null;
        try {
            Net.download(new Net.Task("http://127.0.0.1:1/x/loader-4.0.44.jar", dir.resolve("a.jar"), null, -1), n -> {});
        } catch (IOException e) {
            err = e;
        }
        check("тип HostsUnavailableException", err instanceof Net.HostsUnavailableException);

        String shown = LauncherApp.errorText(err);
        check("есть имя файла: " + shown, shown.contains("loader-4.0.44.jar"));
        check("есть про прокси: " + shown, shown.toLowerCase().contains("прокси"));
        check("есть «Повторить»: " + shown, shown.contains("Повторить"));
        check("нет java.net.: " + shown, !shown.contains("java.net."));

        String other = LauncherApp.errorText(new IOException("Игра завершилась с кодом 1"));
        check("прочие ошибки без изменений: " + other, other.equals("Игра завершилась с кодом 1"));

        if (failed > 0) { System.out.println(failed + " FAILED"); System.exit(1); }
        System.out.println("OK");
        System.exit(0);
    }
}
