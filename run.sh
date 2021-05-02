#!/usr/bin/env bash

pluginText="
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <executions>
                    <execution>
                        <goals>
                            <goal>java</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <mainClass>com.ealax.paysim.PaySim</mainClass>
                </configuration>
            </plugin>"

# Rename file
cd paysimplus
mv pom.xml pom.xml.save

# Recreate file
linePlugins=$(awk '/<\/plugin>/ { print NR }' pom.xml.save)
prevLine=0

while IFS= read -r numLine; do
    text=$(awk "(NR > $prevLine)" pom.xml.save)
    numberAdjusted=$(("$numLine" - "$prevLine"))
    echo "$text" | head -n "$numberAdjusted" >> pom.xml

    # Update variable
    prevLine=$numLine
done <<< "$linePlugins"

echo "$pluginText" >> pom.xml

# Add final line
numLines=$(awk 'END { print NR }' pom.xml.save)
lastLine=$(("$numLines" - "$prevLine"))
tail -n "$lastLine" pom.xml.save >> pom.xml

# Compile
mvn package --quiet
mvn exec:java --quiet

# Restore pom file
mv pom.xml.save pom.xml
cd ..
echo 'END'
