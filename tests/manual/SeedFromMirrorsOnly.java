package test;

import com.elium.launcher.GameInstaller;
import com.elium.launcher.Net;
import java.nio.file.Path;
import java.util.List;

/**
 * Ручная проверка (не входит в test.ps1): скачать библиотеки установщика
 * ТОЛЬКО с зеркал, как будто maven.neoforged.net и libraries.minecraft.net
 * заблокированы. Аргументы: <installer.jar> <gameDir>.
 */
public class SeedFromMirrorsOnly {
    public static void main(String[] args) throws Exception {
        Path jar = Path.of(args[0]);
        Path game = Path.of(args[1]);
        List<Net.Task> tasks = GameInstaller.installerLibraryTasks(jar, game.resolve("libraries"));
        Net.resetHostOverrides();
        int i = 0;
        for (Net.Task t : tasks) {
            List<String> alts = com.elium.launcher.Mirrors.alternatives(t.url());
            String blocked = "http://127.0.0.1:1/blocked/" + (i++);
            for (String a : alts) Net.addMirrorForTesting(blocked, a);
            Net.download(new Net.Task(blocked, t.target(), t.sha1(), t.size()), n -> {});
        }
        System.out.println("seeded " + tasks.size() + " from mirrors only");
        System.exit(0);
    }
}
