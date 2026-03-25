-- export-inventory.applescript
-- Exports a Numbers file to CSV, normalizing the `img` column to basenames only
--
-- Usage:
--   osascript export-inventory.applescript <input.numbers> <output.csv>

use scripting additions

on run argv
    if (count of argv) is not 2 then
        log "Usage: osascript export-inventory.applescript <input.numbers> <output.csv>"
        error "Expected 2 arguments: input Numbers file and output CSV path" number 1
    end if

    set numbersFilePath to do shell script "realpath " & quoted form of (item 1 of argv)
    set csvFilePath to do shell script "cd $(dirname " & quoted form of (item 2 of argv) & ") && pwd"
    set csvFilePath to csvFilePath & "/" & (do shell script "basename " & quoted form of (item 2 of argv))

    set csvLines to {}

    tell application "Numbers"
        open POSIX file numbersFilePath

        tell document 1
            tell sheet 1
                tell table 1
                    set numRows to row count
                    set numCols to column count

                    -- Find the index of the `img` column from the header row
                    set imgColIndex to -1
                    repeat with c from 1 to numCols
                        set hdr to value of cell 1 of column c
                        if hdr is not missing value and (hdr as text) is "img" then
                            set imgColIndex to c
                        end if
                    end repeat

                    -- Read all rows into CSV lines
                    repeat with r from 1 to numRows
                        set rowParts to {}
                        repeat with c from 1 to numCols
                            set cellVal to value of cell r of column c
                            if cellVal is missing value then
                                set cellStr to ""
                            else
                                set cellStr to cellVal as text
                            end if

                            -- Normalize img column to basename (skip header row)
                            -- If value is a bare number, expand to IMG_<n>.jpg to match image filenames
                            if c = imgColIndex and r > 1 and cellStr is not "" then
                                if cellStr does not contain "." then
                                    set cellStr to "IMG_" & cellStr & ".jpg"
                                else
                                    set cellStr to do shell script "basename " & quoted form of cellStr
                                end if
                            end if

                            set end of rowParts to my csvEscape(cellStr)
                        end repeat
                        set end of csvLines to my joinWith(rowParts, ",")
                    end repeat
                end tell
            end tell
        end tell

        close document 1
    end tell

    -- Write CSV via Python for reliable UTF-8 output
    set csvContent to my joinWith(csvLines, linefeed)
    set tempFile to "/tmp/inventory_export_" & (do shell script "date +%s") & ".csv"
    set fileRef to open for access POSIX file tempFile with write permission
    set eof of fileRef to 0
    write csvContent to fileRef as «class utf8»
    close access fileRef
    do shell script "mv " & quoted form of tempFile & " " & quoted form of csvFilePath

    log "Exported " & (count of csvLines) & " rows to " & csvFilePath
end run

-- Wraps a value in quotes if it contains commas, quotes, or newlines
on csvEscape(val)
    if val contains "," or val contains "\"" or val contains linefeed or val contains return then
        set val to my replaceIn(val, "\"", "\"\"")
        return "\"" & val & "\""
    end if
    return val
end csvEscape

on replaceIn(str, find, repl)
    set AppleScript's text item delimiters to find
    set parts to text items of str
    set AppleScript's text item delimiters to repl
    set joined to parts as text
    set AppleScript's text item delimiters to ""
    return joined
end replaceIn

on joinWith(lst, delim)
    set AppleScript's text item delimiters to delim
    set joined to lst as text
    set AppleScript's text item delimiters to ""
    return joined
end joinWith
