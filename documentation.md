Introduction
============

This document may be used as support for the design and development of the MEO Cloud desktop application.

Currently, the MEO Cloud desktop application has three main components:

1.	GUI
1.	File Manager Extension
1.	Synchronization Core (a.k.a. "sync core" or just "core")

The GUI and File Manager Extension components provide the user-visible part of the application. The GUI controls every aspect of the sync core’s functionality. The File Manager Extension improves the application’s integration with Desktop Managers by providing a contextual menu and status overlay icons for each file in the synchronized folder.

On the other hand, the synchronization core keeps the contents of the MEOCloud folder (on the file system) synchronized with the MEO Cloud service.

Architecture Overview
=====================

The following image provides a high-level picture of the desktop GUI application architecture. Note that the interface between the File Manager Extension and the Sync Core is subject to continuous development as we add new features.

![MEO Cloud GUI Overview] (https://cld.pt/dl/download/f69b0d8b-07f2-414d-887a-6480537c42c1/architecture.png?public=f69b0d8b-07f2-414d-887a-6480537c42c1)

Gray-colored components (GUI and File Manager Extension) are native operating system specific applications (Linux, Windows, Mac OS X, etc.). The sync core component is a multiplatform application and is available in binary compiled form. Interaction with the core is described in the following sections.

The specific `<transport>` used depends on the operating system where the application is running: Unix sockets on Linux and OS X, and Windows named pipes on Windows.

A CLI Python-based reference implementation is provided in [MEO Cloud CLI Repository](http://127.0.0.1) and may be used to create a working GUI. Communication between the core and the UI is implemented in the `client/linux/daemon` directory.

Runtime Interactions
====================

The GUI starts and stops the sync core. Moreover, the GUI is expected to provide a watchdog-like functionality for the core. Should the core be terminated unexpectedly (crash, process kill), the GUI must restart the core.

If, after multiple restart attempts the core keeps terminating, the GUI should stop the watchdog mechanism and notify the user that the application is unable to start properly.

The core provides a **ping** mechanism that can be used to determine if it is alive.  Currently, a five second interval between pings is recommended. Additionally, the GUI should check the return code of the system call used to start the core.

Startup
-------

The GUI should ensure that no other core instances are running. This can be achieved by acquiring a single core instance lock, as described in [Startup on Linux and Mac OS X](#startup-on-linux-and-mac-os-x) and [Startup on Windows](#startup-on-windows).

The core process itself will look for the following environment variables during startup:

-	`CLD_CORE_SOCKET_PATH` – contains the name of the Unix socket or Windows named pipe where the core should provide its thrift service
-	`CLD_UI_SOCKET_PATH` – contains the name of the Unix socket or Windows named pipe where the GUI should provide its thrift service

The GUI must set these two environment variables before starting the core process.

### Startup on Linux and Mac OS X
The GUI must try to obtain an exclusive lock on the `~/.meocloud/daemon.lock` file, using `lockf(3)`, before starting the core. Also, it must ensure that only the user that started the application has permissions to connect to the created Unix sockets.

If the lock cannot be obtained, the GUI should read the core’s PID from the `~/.meocloud/daemon.pid` file and terminate it before attempting to acquire the lock again.


#### Lauching the core process on Linux

The following Python code snippet exemplifies how to launch the core process on Linux. We recommend that `ui_socket`, `core_socket` and `shell_socket` are placed in the `~/.meocloud` directory.

```python
core_env = os.environ.copy()
core_env['CLD_CORE_SOCKET_PATH'] = <core_socket>
core_env['CLD_UI_SOCKET_PATH'] = <ui_socket>
core_env['CLD_SHELL_SOCKET_PATH'] = <shell_socket>
process = Popen(['/path/to/meocloudd'], env=core_env)
```

#### Launching the core process on Mac OS X

The following Objective-C code snippet exemplifies how to launch the core process on OS X. We recommend that `ui_socket`, `core_socket` and `shell_socket` are placed in the per-user temporary area.

```objective-c
  NSTask *task = [[NSTask alloc] init];    
  NSMutableDictionary *environment = [[[NSProcessInfo processInfo] environment] mutableCopy];

  [environment addEntriesFromDictionary:@{
    @"CLD_UI_SOCKET_PATH": @"</path/to/ui_socket>",
    @"CLD_CORE_SOCKET_PATH": @"</path/to/core_socket>",
    @"CLD_SHELL_SOCKET_PATH": @"</path/to/shell_socket>",
  }];
    
  [task setEnvironment:environment];
  [task setLaunchPath:@"</path/to/meocloudd>"]];
  [task launch];
```

### Startup on Windows
The GUI must create the `MEOCloud_044230DF-3CD1-4A3D-8A63-ADDF0255400F` mutex (see: [CreateMutex](http://msdn.microsoft.com/en-us/library/windows/desktop/ms682411\(v=vs.85\).aspx)) before starting the core. If the mutex cannot be created, the GUI should read the core’s PID from the `%LOCALAPPDATA%\daemon.pid` file and terminate it before attempting to create the mutex again.

Care must be taken when generating Windows named pipe names. Names should be randomly generated using entropy from a source approved for cryptographic purposes. Converting a 16-byte output from the [CryptGenRandom](http://msdn.microsoft.com/en-us/library/windows/desktop/aa379942\(v=vs.85\).aspx) function to a hexadecimal string should be sufficient.

#### Lauching the core process on Windows

The following C code snippet exemplifies how to launch the core process on Windows. Please ensure that the Windows Named Pipe names are created according to rules described [above](#startup-on-windows).

```C
STARTUPINFO startupInfo; 
PROCESS_INFORMATION processInfo; 
DWORD creationflags = CREATE_UNICODE_ENVIRONMENT | CREATE_NO_WINDOW; 
LPTSTR processcmd  = _tcsdup(TEXT("<Path\To\meocloudd.exe>")

SetEnvironmentVariable(TEXT("CLD_CORE_PIPE"), TEXT("\\.\pipe\<core_pipe>"));
SetEnvironmentVariable(TEXT("CLD_UI_PIPE"), TEXT("\\.\pipe\<ui_pipe>"));
SetEnvironmentVariable(TEXT("CLD_SHELL_PIPE"), TEXT("\\.\pipe\<shell_pipe>"));

ZeroMemory(&SsartupInfo, sizeof(startupInfo));
startupInfo.cb = sizeof(startupInfo);
BOOL result = CreateProcess(NULL, processcmd, NULL, NULL, FALSE, creationflags, NULL, NULL, &startupInfo, &processInfo);
```

### Examples

Some common interaction scenarios between the GUI and Core are detailed. It is assumed that the GUI has already started the core with the required environment variables set.

#### Registration

The GUI stores the user credentials for the MEO Cloud service. These credentials must be stored using a secure mechanism, preferably provided by the desktop environment itself, such as the [Gnome Keyring](https://wiki.gnome.org/action/show/Projects/GnomeKeyring), [MacOS Keychain](https://developer.apple.com/library/mac/documentation/security/Reference/keychainservices/Reference/reference.html) or the [Windows Data Protection API](http://msdn.microsoft.com/en-us/library/ms995355.aspx).

Note that the Core starts its service in ```CLD_CORE_SOCKET_PATH``` and connects to the GUI service in ```CLD_UI_SOCKET_PATH```. 
![Registration](https://cld.pt/dl/download/4af0618d-1db2-4cda-be02-ce3ca52f240f/registration.png)


#### Selective Sync
![Selective Sync](https://cld.pt/dl/download/0bfe4cbb-7514-414d-8810-09c3ae951592/selective_sync.png)

#### Pausing
![Pausing](https://cld.pt/dl/download/88fc1dde-20cc-47ae-8a57-2f8ed11f961e/pausing.png)

Protocols
=========

UI Protocol
-----------

### Thrift specification

```thrift
enum NotificationLevel {
  INFO
  WARNING
  ERROR
}

enum State {
  INITIALIZING
  AUTHORIZING
  WAITING
  SYNCING
  READY
  PAUSED
  ERROR
  SELECTIVE_SYNC
  RESTARTING
  OFFLINE
}

struct UserNotification {
  1: i32 code,
  2: i32 type,
  3: NotificationLevel level = NotificationLevel.INFO,
  4: list<string> parameters,
}

struct SystemNotification {
  1: i32 code,
  2: list<string> parameters,
}

struct SyncStatus {
  1: i32 uploadRate,
  2: i32 downloadRate,
  3: i32 pendingUploads,
  4: i32 pendingDownloads,
  5: i32 uploadETASecs,
  6: i32 downloadETASecs,
  7: i32 pendingIndexes,
}

struct Status {
  1: State state,
  2: i32 statusCode,
  3: i64 usedQuota,
  4: i64 totalQuota,
}

struct NetworkSettings {
  1: string proxyAddress,
  2: string proxyType,
  3: i32 proxyPort,
  4: string proxyUser,
  5: string proxyPassword,
  6: i32 uploadBandwidth,
  7: i32 downloadBandwidth,
}

struct DesktopSettings {
  1: bool autostart,
  2: bool notifications,
  3: bool blackIcons
}

struct UserSettings {
  1: NetworkSettings network,
  2: DesktopSettings desktop,
  3: string rootFolder
}

struct Account {
  1: string clientID,
  2: string authKey,
  3: string email,
  4: string name,
  5: string deviceName,
}

service Core {
  Status currentStatus();
  SyncStatus currentSyncStatus();
  list<string> recentlyChangedFilePaths();
  UserSettings migratedSettings();
  void pause();
  void unpause();
  void shutdown();
  string authorizeWithDeviceName( 1: string deviceName );
  void startSync( 1: string rootFolder );
  void unlink( 1: Account account);
  void notify( 1: SystemNotification note );
  void networkSettingsChanged( 1: NetworkSettings settings );
  void requestRemoteDirectoryListing( 1: string path );
  list<string> ignoredDirectories();
  void setIgnoredDirectories( 1: list<string> paths );
  string webLoginURL();
  bool ping();
  string version();
}

service UI {
  NetworkSettings networkSettings();
  void beginAuthorization();
  void authorized( 1: Account account );
  void endAuthorization();
  Account account();
  void notifySystem( 1: SystemNotification note );
  void notifyUser( 1: UserNotification note );
  void remoteDirectoryListing( 1: i32 statusCode, 2: string path, 3: list<string> listing );
}
```

### Status and Notification Codes

The core will send a `UserNotification` or `SystemNotification` to the GUI whenever certain events occur. For example, an event will be sent if the core cannot update a file on the file system due to insufficient permissions:

```C
UserNotification {
  code:  CLDUserNotificationCannotSyncDueToPermissions,
  type:  CLDUserNotificationTypeMaskPersistent|CLDUserNotificationTypeMaskMenuBar,
  level: NotificationLevel.INFO,
  parameters: <path>
}
```

#### System Notification Codes

System notifications (`SystemNotification`) are sent whenever the core and GUI want to communicate with each other.

```C
typedef enum {
  CLDSystemStatusChanged = 0,
  CLDSystemNetworkSettingsChanged,
  CLDSystemSharedFolderAdded,
  CLDSystemSharedFolderUnshared
} CLDSystemNotificationCode;
```

**Messages from the Core to the GUI**

- `CLDSystemStatusChanged` – core status has changed. The GUI should query the new status using the `currentStatus()` call;
- `CLDSystemSharedFolderAdded` – a shared folder was created. The first parameter contains the relative shared folder path. The GUI must add a "Shared Folder" icon to this folder;
- `CLDSystemSharedFolderUnshared` – a shared folder was unshared. The first parameter contains the relative shared folder path.

**Messages from the GUI to the Core**
- `CLDSystemNetworkSettingsChanged` – the network settings have changed.

#### User Notification Codes

User notifications (`UserNotification`) are sent from the core to the GUI. These notifications should be displayed to the user, using the strings in [User Notification Messages](#user-notifications-messages).

```C
typedef enum {
  CLDUserNotificationFileAdded = 200,
  CLDUserNotificationFileDeleted,
  CLDUserNotificationFileUpdated,
  CLDUserNotificationFilesAdded,
  CLDUserNotificationFilesDeleted,
  CLDUserNotificationFilesUpdated,
  CLDUserNotificationFilesChanged,

  CLDUserNotificationSharedFolderAdded = 250,
  CLDUserNotificationSharedFolderDeleted,
  CLDUserNotificationSharedFolderUnshared,
    
  CLDUserNotificationQuotaExceeded = 500,
  CLDUserNotificationCannotSyncDueToSpace,
  CLDUserNotificationCannotSyncDueToPermissions
} CLDUserNotificationCode;
```

####	User Notification types
Notification types specify where and how a `UserNotification` should be displayed to the user. `CLDUserNotificationTypeMaskGrowl`, should be displayed as a pop-up notification.

```C
typedef enum {
  CLDUserNotificationTypeReset            = 0,
  CLDUserNotificationTypeMaskPersistent   = 1 << 0,
  CLDUserNotificationTypeMaskMenuBar      = 1 << 1,
  CLDUserNotificationTypeMaskAlertWindow  = 1 << 2,
  CLDUserNotificationTypeMaskGrowl        = 1 << 3,
} CLDUserNotificationType;
```

If a notification type has the `CLDUserNotificationTypeMaskPersistent` bit set, the notification must be shown until a notification with the same code is received with the mask `CLDUserNotificationTypeReset`.

####	Status codes
```C
typedef struct {
  unsigned int syncCode:8;
  unsigned int :16;
  unsigned int errorCode:8;
} CLDStatusCode;

typedef enum {
  CLDStatusNoError,
  CLDStatusErrorAuthTimeout,
  CLDStatusErrorRootFolderGone,
  CLDStatusErrorUnknown,
  CLDStatusErrorThreadCrash,
} CLDStatusErrorCore;
```

####	Status mask

```C
typedef enum {
  CLDSyncStatusMaskIndexing       = 1 << 0,
  CLDSyncStatusMaskUploading      = 1 << 1,
  CLDSyncStatusMaskDownloading    = 1 << 2,
  CLDSyncStatusMaskListingChanges = 1 << 3,
} CLDSyncStatusMask;
```

###	User Notifications Messages

```Python
# File creations and deletions
"200_title" = "File Added"
"200_description" = "File \"%S\" was added to your APP_NAME folder"
"201_title" = "File Removed"
"201_description" = "File \"%S\" was removed from your APP_NAME folder"
"202_title" = "File Updated"
"202_description" = "File \"%S\" was updated in your APP_NAME folder"
"203_title" = "Files Added"
"203_description" = "%S files were added to your APP_NAME folder"
"204_title" = "Files Removed"
"204_description" = "%S files were removed from your APP_NAME folder"
"205_title" = "Files Updated"
"205_description" = "%S files were updated in your APP_NAME folder"
"206_title" = "Files Synchronized"
"206_description" = "%S files were synchronized in your APP_NAME folder"
"207_title" = "Connecting to APP_NAME..."
"207_description" = "Please check your Internet connection and proxy settings."

# Shared folders
"250_title" = "Shared Folder Created"
"250_description" = "Shared folder \"%S\" was created in your APP_NAME folder"
"251_title" = "Shared Folder Deleted"
"251_description" = "Shared folder \"%S\" was deleted from your APP_NAME folder"
"252_title" = "Shared Folder Unshared"
"252_description" = "Stopped sharing folder \"%S\""

# Errors
"500_title" = "Quota Exceeded"
"500_description" = "You have exceeded your APP_NAME quota. Please free more space to continue uploading."
"501_title" = "Could not synchronize \"%S\""
"501_description" = "Could not synchronize \"%S\". Please verify that you have sufficient permissions and that the file is not in use."
"502_title" = "Insufficient disk space"
"502_description" = "Could not update \"%S\". Please ensure that you have sufficient free disk space."
"503_title" = "File \"%S\" is in use"
"503_description" = "File \"%S\" is in use. Please ensure that the file is not open by another application."
```

File Manager Extension Protocol
-------------------------------

**This protocol is currently being finalized and may change.**

### Thrift specification

```thrift
enum NotificationType {
  FILE_STATUS
}

enum FileState {
  READY
  SYNCING
  IGNORED
  ERROR
}

enum MessageType {
  SUBSCRIBE_PATH
  SHARE
  OPEN
  FILE_STATUS
}

enum SubscribeType {
  SUBSCRIBE
  UNSUBSCRIBE
}

enum ShareType {
  LINK
  FOLDER
}

enum OpenType {
  BROWSER
}

enum FileStatusType {
  REQUEST
  RESPONSE
  MULTI_REQUEST
  MULTI_RESPONSE
}

struct SubscribeMessage {
  1: SubscribeType type,
  2: string path,
}

struct ShareMessage {
  1: ShareType type,
  2: string path,
}

struct OpenMessage {
  1: OpenType type,
  2: string path,
}

struct FileStatus {
  1: string path,
  2: FileState state,
}

struct FileStatusMessage {
  1: FileStatusType type,
  2: optional FileStatus status,
  3: optional list<FileStatus> statuses,
}

struct Message {
  1: MessageType type,
  2: optional SubscribeMessage subscribe,
  3: optional ShareMessage share,
  4: optional OpenMessage open,
  5: optional FileStatusMessage fileStatus,
}
 ```
