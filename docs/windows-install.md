# synthtwin on a Windows computer without internet

This page is for the person who runs synthtwin on a protected Windows
computer: a computer with no internet, where nothing may be installed,
that holds the real table. It covers the **ready folder**: one zip file
that holds synthtwin, its own Python and every library it needs. You
unzip it and double-click a file. Nothing is installed and no
administrator is needed; section 10, "What it writes", lists every place
synthtwin writes on the computer.

The zip is made and tried out by the project's public build service on
each change to what the folder is made from (the workflow
`windows-bundle.yml`, plan P4-D483): it is unzipped on a clean Windows
computer with the network refused, and the steps on this page are run
there as a person types them. Only a zip that passed is kept, for 90
days, as a download named `synthtwin-windows-ready` on that run's page.
Its first run is owed to the push that carries it; STATE names the first
green run. Whoever looks after synthtwin for you downloads it and gives
it to you with the SHA-256 the run prints: the first step of section 2
checks the zip against that value before anything in it runs.

## 1. What you need

- **The zip file**, named like `synthtwin-0.1.0-windows-ready.zip`,
  copied to a USB key or handed over as your institution allows. Keep it
  as one file: do not unzip it on the way.
- **Windows 10 or 11, 64-bit, on an Intel or AMD processor.** To check:
  Start, Settings, System, About. "System type" should read "64-bit
  operating system, x64-based processor". A computer with an Arm
  processor runs the folder more slowly, and synthtwin says so when it
  starts.
- **Enough memory.** Write down the computer's memory and processors:
  press Ctrl+Shift+Esc to open Task Manager, choose Performance, then
  **Memory** (the total is at the top right) and **CPU** ("Cores" and
  "Logical processors"). synthtwin's own computer check cannot read the
  memory on Windows, so these numbers are yours to keep. For a table of
  2,000,000 rows by 50 columns, use a computer with at least 16 GB of
  memory, and close other programs.
- **Free disk space**: about 1 GB for the folder, plus about three times
  the size of your table for synthtwin's files.
- **Your table**, saved as a CSV file: the final analysis table, at
  least 20,000 rows and, where patients have several rows, at least
  1,000 patients. synthtwin makes twins of large tables only and refuses
  anything smaller. From Excel: File, Save As, "CSV UTF-8 (Comma
  delimited)". After that, **never open and save the CSV in Excel again**
  before synthtwin reads it: Excel rewrites codes such as `0250` and
  dates in its own way.

No internet, no administrator rights and no Python are needed: the
folder carries its own.

## 2. Put the folder in place (once)

1. **Copy the zip file from the USB key into the computer, then check
   it before you unzip it.** Whoever gave you the zip also gave you its
   SHA-256: a line of 64 letters and digits, printed on the page of the
   run that kept the zip. Open the folder that holds the zip, click the
   folder's address bar, type `powershell` and press Enter: a PowerShell
   window opens in that folder. Copy this line into it and press Enter:

   ```
   Get-FileHash -Algorithm SHA256 .\synthtwin-*-windows-ready.zip
   ```

   The long line under `Hash` must be the SHA-256 you were given, every
   letter and digit (capitals or not does not matter). If it is not, do
   not unzip the zip: ask for it again. (Where PowerShell is blocked,
   type `certutil -hashfile` and the zip's name, then `SHA256`, in
   Command Prompt.)
2. If the zip was downloaded from the internet **on this computer**:
   right-click it, choose Properties, tick **Unblock**, then OK. (A zip
   copied from a USB key needs nothing.)
3. Right-click the zip and choose **Extract All**. Type a short place:
   `C:\` (or `C:\Users\YOU\`, with your own user name), and choose
   Extract. A folder named like `synthtwin-0.1.0-win` appears there.
   Extract All writes about 8,400 files and can take several minutes
   when the computer's virus scanner is on: wait for it to finish
   before you open the folder.

**Why the zip is checked first.** Each time it starts, START-HERE checks
every file of the folder against its list of hashes, and that catches a
folder damaged on its way or changed by accident. It cannot catch a
folder someone changed on purpose: the folder's own Python and the
check itself run before any file is compared, so a deliberately changed
copy of them could skip the check. The SHA-256 you compare in step 1
comes from outside the zip, so it covers those files too.

**Why a short place.** Windows refuses file paths of 260 characters or
more unless an administrator turned that limit off. The folder is built
so that every path in it fits under any place of up to 99 characters
(100 with its separator), and `C:\` or your own folder is far shorter.
Never unzip it into a OneDrive folder or onto a network drive.

## 3. Make your work folder

Make a folder named `twin-work` in your own folder,
`C:\Users\YOU\twin-work`, and copy your table into it. synthtwin writes
its files beside the table, so they all stay together there.

**Not Documents, Desktop, Pictures, OneDrive or a network drive.**
synthtwin reads only from this computer's own disk: it refuses a path
that leads through a link or to a network location, and on many
computers Documents and Desktop are folders that OneDrive keeps in step
with the cloud, which Windows marks as links. Those folders may also be
protected against programs writing in them ("controlled folder
access"). `C:\Users\YOU\twin-work` avoids all of that.

## 4. Start synthtwin

Open the unzipped folder and double-click **START-HERE**.

What you should see:

1. A black window that reads every file of the folder once and checks it
   against its list of hashes (`SHA256SUMS`). This can take a minute or
   more, since the folder holds about 8,400 files and the computer's
   virus scanner may look at each one; the window prints how many
   seconds it took.
2. Then a **PowerShell** window opens in your `twin-work` folder (if it
   exists), shows how to use it, and runs the computer check: a
   column of lines marked `ok`, one marked `note` saying the memory
   could not be read (expected on Windows), and "Every check that could
   be made passed".

Where PowerShell is blocked on the computer, a **Command Prompt**
window opens instead and works the same way. One difference there:
synthtwin prints the commands it suggests in PowerShell's quoting, so
where it shows a name between single quotes `'like this'`, type it
between double quotes `"like this"`, and where two single quotes stand
together inside it, as in `'Crohn''s disease'`, type one: `"Crohn's
disease"`. The window's first lines say the same.

If START-HERE says a file "does not match its hash in SHA256SUMS", the
folder was changed or damaged after it was made: unzip the zip file
again into a new folder and start from there. If it says a file "could
run it in place of synthtwin's own launcher", a program file was saved
into synthtwin's folder: unzip the zip again into a new folder and keep
your own files in `twin-work`. If it says to unzip the
zip first, you opened START-HERE inside the zip without Extract All: do
step 3 of section 2, then double-click START-HERE in the unzipped
folder.

The window is yours until you close it. It keeps no history of what you
type (not yet measured on Windows); synthtwin's own files stay beside
the table. Next time, double-click START-HERE again.

## 5. The commands

Type each command in the synthtwin window and press Enter. If the window
did not open in your work folder, go there first:

```
cd $HOME\twin-work
```

**Check the computer against your table** (it never opens the table; it
asks Windows for the file's size):

```
synthtwin doctor my-table.csv
```

**Describe your table**, naming the column that says which patient each
row is about (here `subject_id`):

```
synthtwin profile my-table.csv --identifier subject_id
```

For a large table the screen can stay still for a long time while
synthtwin reads: that is normal. When it asks a question on the screen,
type the number shown in square brackets and press Enter; Enter alone
leaves the question open. **To stop, press Ctrl+C. To end your answers,
press Ctrl+Z, then Enter.**

**Answer the questions left open in the file.** synthtwin writes them
into `my-table-questions.json` beside your table. Open it in Notepad,
write one of the offered answers beside `"your_answer"` (keep the
quotation marks; type them in Notepad, not in a word processor), save
it, and describe the table again with your answers:

```
synthtwin profile my-table.csv --identifier subject_id --answers my-table-questions.json --replace
```

An answer can bring a new question (a column of five-figure codes
answered `code` is then asked whether its values could be ZIP codes):
answer it the same way and run the same command again.

**Read the description** in `my-table-profile.txt`, in Notepad, before
anything leaves the computer: its section "WHAT THIS PROFILE CARRIES
FROM YOUR TABLE" names every column whose real values it carries.

## 6. Long runs

A table of millions of rows can take hours to describe. Before a long
run:

- keep the computer plugged in, with the lid open and the synthtwin
  window open (a screen lock is fine);
- choose a day without a planned restart for updates;
- **do not click inside the window while synthtwin works.** In the
  classic Windows console a click starts a selection and *pauses* the
  program until the selection ends. If the window's title begins with
  the word **Select**, press Esc and synthtwin goes on.

Closing the window stops synthtwin; nothing half-written is left as if
it were finished.

## 7. If something stops

Each message below names what to do; in each case nothing was written,
so it is safe to correct and run again.

- **START-HERE: "does not match its hash in SHA256SUMS" or "is listed
  in SHA256SUMS but missing".** Unzip the zip again into a new folder.
- **START-HERE: "could run it in place of synthtwin's own launcher".**
  A program file was saved into synthtwin's folder: unzip the zip again
  into a new folder, and keep your own files in `twin-work`.
- **START-HERE: "Unzip synthtwin's zip first".** START-HERE was opened
  inside the zip: right-click the zip, Extract All (section 2), then
  double-click START-HERE in the unzipped folder.
- **START-HERE: "START-HERE takes no file".** A table was dropped on it:
  double-click START-HERE alone, then type the commands in the window it
  opens.
- **"Windows protected your PC".** The zip was downloaded on this
  computer and not unblocked: delete the folder, unblock the zip
  (section 2) and unzip it again. If your institution does not allow
  that, ask IT (section 10).
- **"This program is blocked by group policy", "Access is denied" or
  "blocked by your system administrator".** The computer's rules do not
  allow programs in your own folders. IT can place the folder under
  `C:\Program Files` (section 10).
- **"The command prompt has been disabled by your administrator".**
  START-HERE cannot run on that computer. Open PowerShell from the Start
  menu and type this on one line, with the folder's real place in each
  of its three places. It runs the same check of every file that
  START-HERE runs and, only when the folder passes, opens the synthtwin
  window; if that is blocked too, ask IT:

  ```
  & 'C:\synthtwin-0.1.0-win\python\python.exe' -I -B 'C:\synthtwin-0.1.0-win\scripts\check_folder.py' --start 'C:\synthtwin-0.1.0-win'
  ```
- **"was not accepted ... is a link" or "... a network location".** The
  table is in a synced, linked or network folder: copy it into
  `C:\Users\YOU\twin-work` (section 3).
- **"could not be written ... the file is not open in another
  program".** Close the file in Excel (or any other program) and run the
  command again.
- **"synthtwin makes twins of large tables only".** The table is under
  20,000 rows or, with several rows a patient, under 1,000 patients:
  describe the whole extract rather than a sample.
- **"something is already at one of the names it would write".** Add
  `--replace` at the end of the same command, or move the old files
  away.
- **"Please type one of the numbers offered" after pressing Ctrl+D.**
  On Windows the end of your answers is Ctrl+Z, then Enter.
- **The window seems frozen.** Look at its title: if it begins with
  Select, press Esc (section 6).

## 8. What may leave the protected computer

**Only the description, `my-table-profile.json`, and only after your
institution's approval.** It is the one file the twin is built from. It
holds no row of your table, but it is not anonymous: it names your
columns and holds counts, labels and summaries computed from your real
data. Your institution's rules for material derived from real data
apply to it.

Read `my-table-profile.txt`, the same description in words, on the
protected computer; it stays there with `my-table-questions.json`,
which you need for every later run.

Every file a full run writes carries facts computed from the real
table, so the same rules apply to each of them, on any computer. The
table itself, and any part, sample or copy of it, never leaves.

## 9. On the other computer: the twin

On a computer of your own (a Mac, or any computer with synthtwin
installed from its bundle, as the project's README says), build the
twin from the description:

```
synthtwin generate my-table-profile.json --seed 7
```

and measure the twin against the description:

```
synthtwin validate my-table-profile.json --twin my-table-twin.csv
```

Write and test your analysis code on `my-table-twin.csv`; it is meant to
run unchanged on the real table, back on the protected computer.

## 10. For IT

**What it is.** One folder: synthtwin, python.org's embeddable Python
3.14 for Windows x64 (its programs signed by the Python Software
Foundation, its Visual C++ runtime files by Microsoft) and the libraries
numpy, pandas, pyarrow, scipy, python-dateutil, six and tzdata,
installed into `python\lib` when the folder was built in the project's
public CI run, from the project's hash-pinned
`requirements-install.lock`, with every wheel's SHA-256 checked (pip
install `--isolated --no-index --require-hashes --only-binary=:all:
--target`). `BUILD-INFO.txt` names the commit, the Python release and
every wheel with its SHA-256; `THIRD-PARTY-NOTICES.txt` holds every
library's licence and Python's own.

**What it does.** It opens no network connection and installs nothing.
`START-HERE.bat` runs `scripts\check_folder.py` with the folder's
`python.exe`: every file is checked against `SHA256SUMS`, and a changed
or missing file, or an extra program file outside `python\` (`.exe`,
`.bat`, `.cmd`, `.ps1` and the other endings `PATHEXT` runs), is refused
before synthtwin starts. Then it opens `powershell.exe -NoLogo
-NoProfile -NoExit -Command` (no script file, no change of execution
policy) with a function named `synthtwin`, or, where PowerShell is
blocked, `cmd.exe` with a DOSKEY macro binding the word `synthtwin` to
the folder's `synthtwin.bat`, the folder first on `PATH` and
`NoDefaultCurrentDirectoryInExePath` set, for that window only. Every
command either window runs names `synthtwin.bat` or `python.exe` by its
full path, so a program named `synthtwin` in the work folder never runs
in its place.

**The trusted start.** The check guards against damage and accidental
change. It does not guard against a deliberate change of the folder:
`python.exe`, the DLLs and standard library it loads first and the
check itself run before any hash is compared. The zip's own SHA-256,
printed by the build run and compared with `Get-FileHash` before the
zip is unzipped (section 2, step 1), covers the folder as a whole.

Its only `.exe` files are `python.exe` and
`pythonw.exe` as python.org ships them, signed; the libraries' own
`.pyd` and `.dll` files are those of their wheels, each wheel checked by
its SHA-256 against the lock.

**What it writes.** synthtwin writes only beside the table the person
names, in the folder given with `--out-dir`, or, for the computer
check's test file, removed at once, in the window's current folder. It
writes no registry key, no environment variable and nothing inside its
own folder (its Python runs with `-I -B`, every library was compiled
when the folder was built, and `python314._pth` limits what it loads to
`python314.zip`, `python\` and `python\lib`), and the PowerShell window
turns off PSReadLine's history file, so what is typed there is not saved
(not yet measured on Windows).

**How to verify it.** In PowerShell: `Get-FileHash -Algorithm SHA256`
on the zip before it is unzipped, against the SHA-256 the build run's
summary prints; then on any file, against `SHA256SUMS`;
`Get-AuthenticodeSignature` on
`python\python.exe` and the `.dll` and `.pyd` files beside it (or
right-click, Properties, Digital Signatures); `BUILD-INFO.txt` against
the public CI run that built the folder, which keeps a zip only after
rehearsing it on a clean Windows computer with the network refused, and
whose summary prints the zip's SHA-256.

**Where it may live.** Any local disk, including
`C:\Program Files\synthtwin`: it needs no write access to its own
folder, and application-control rules usually allow programs there.

**Removing it.** Delete the folder; "What it writes" above lists
everything else synthtwin may leave on the computer (the files beside
the table are the person's own).

## 11. The backup route

If the ready folder cannot run on the computer, the same run keeps a
second download, `synthtwin-windows-fallback`: the wheelhouse bundle
(the libraries for Python 3.11 to 3.14, with `install.bat`) and
python.org's Python 3.14 installer, with a note, `READ-ME-FIRST.txt`.
It needs a Python installed: run the installer, untick "Use admin
privileges when installing py.exe", tick "Add python.exe to PATH", then
choose "Install Now"; unzip the bundle into a short place and follow
its `INSTALL.txt`, "On Windows", in Command Prompt. This route installs
a private environment and needs it switched on in each new window; the
ready folder needs none of that.
