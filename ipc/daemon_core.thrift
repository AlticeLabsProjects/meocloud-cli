namespace cocoa CLD
namespace py daemon_core
namespace cpp CLD

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
