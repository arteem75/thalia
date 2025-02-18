import org.jetbrains.dokka.gradle.DokkaTask
import java.net.URL

plugins {
    kotlin("jvm") version "1.7.20"
    id("org.jetbrains.dokka") version ("1.7.0")
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(kotlin("stdlib"))
    testImplementation(kotlin("test-junit"))
}

tasks.dokkaHtml.configure {
    dokkaSourceSets {
        configureEach {
            skipDeprecated.set(true)
            documentedVisibilities.set(
                setOf(
                    org.jetbrains.dokka.DokkaConfiguration.Visibility.PUBLIC,
                    org.jetbrains.dokka.DokkaConfiguration.Visibility.PROTECTED
                )
            )
        }
    }
}
