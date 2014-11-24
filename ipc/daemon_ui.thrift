namespace py daemon_ui

enum InitResult {
    AUTHORIZATION_OK
    AUTHORIZATION_REQUIRED
    OFFLINE
    ROOT_FOLDER_MISSING
    TIMEDOUT
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

struct SyncStatus {
    1: i32 uploadRate,
    2: i32 downloadRate,
    3: i32 pendingUploads,
    4: i32 pendingDownloads,
    5: i32 uploadETASecs,
    6: i32 downloadETASecs,
    7: i32 pendingIndexes,
    8: i32 syncCode,
    9: string downloadingPath,
    10: string uploadingPath,
    11: string indexingPath,
}

struct Status {
    1: State state,
    2: i32 statusCode,
    3: i64 usedQuota,
    4: i64 totalQuota,
}

struct StatusResult {
    1: Status status,
    2: SyncStatus syncStatus,
    3: list<string> persistentNotifs,
}

struct RemoteDirectoryListingResult {
     1: i32 statusCode,
     2: string path,
     3: list<string> listing,
}

struct Account {
    1: string clientID,
    2: string authKey,
    3: string email,
    4: string name,
    5: string deviceName,
}

service UI {
    InitResult init();
    InitResult waitForAuthorization();
    string authorizeWithDeviceName( 1: string deviceName );
    void startCore();
    StatusResult status();
    list<string> recentlyChangedFilePaths();
    void pause();
    void unpause();
    void shutdown();
    bool unlink();
    void networkSettingsChanged();
    RemoteDirectoryListingResult remoteDirectoryListing( 1: string path );
    list<string> ignoredDirectories();
    void setIgnoredDirectories( 1: list<string> paths );
    string webLoginURL();
    bool ping();
    string version();
    string coreVersion();
}
