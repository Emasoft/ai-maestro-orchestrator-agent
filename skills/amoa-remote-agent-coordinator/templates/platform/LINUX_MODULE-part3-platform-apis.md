# Linux Platform Module - Platform-Specific APIs

This document covers Linux-specific APIs including inotify file monitoring, D-Bus integration, systemd services, and procfs access.

**Parent Document**: [LINUX_MODULE.md](./LINUX_MODULE.md)

---

## File System Monitoring (inotify)

Monitor file system changes using inotify:

```rust
use inotify::{Inotify, WatchMask, EventMask};
use std::path::Path;

pub struct FileWatcher {
    inotify: Inotify,
}

impl FileWatcher {
    pub fn new(path: &Path) -> Result<Self, Error> {
        let mut inotify = Inotify::init()?;

        inotify.add_watch(
            path,
            WatchMask::MODIFY | WatchMask::CREATE | WatchMask::DELETE,
        )?;

        Ok(Self { inotify })
    }

    pub fn read_events(&mut self) -> Result<Vec<Event>, Error> {
        let mut buffer = [0u8; 4096];
        let events = self.inotify.read_events_blocking(&mut buffer)?;

        // Process events
        {{INOTIFY_IMPL}}
    }
}
```

**Reference**: See `references/linux/inotify_api.md` for complete inotify guide.

---

## D-Bus Integration

Communicate with other processes via D-Bus:

```rust
use zbus::{Connection, dbus_proxy};

#[dbus_proxy(
    interface = "org.freedesktop.Notifications",
    default_service = "org.freedesktop.Notifications",
    default_path = "/org/freedesktop/Notifications"
)]
trait Notifications {
    fn notify(
        &self,
        app_name: &str,
        replaces_id: u32,
        app_icon: &str,
        summary: &str,
        body: &str,
        actions: &[&str],
        hints: &std::collections::HashMap<&str, &zbus::zvariant::Value>,
        expire_timeout: i32,
    ) -> zbus::Result<u32>;
}

pub async fn send_notification(title: &str, message: &str) -> Result<(), Error> {
    let connection = Connection::session().await?;
    let proxy = NotificationsProxy::new(&connection).await?;

    proxy.notify(
        "MyApp",
        0,
        "",
        title,
        message,
        &[],
        &std::collections::HashMap::new(),
        5000,
    ).await?;

    Ok(())
}
```

**Reference**: See `references/linux/dbus_integration.md` for complete D-Bus guide.

---

## systemd Integration

Create a systemd service:

```rust
use systemd::daemon::{notify, STATE_READY, STATE_STOPPING};

pub fn systemd_notify_ready() -> Result<(), Error> {
    notify(false, [(STATE_READY, "1")].iter())?;
    Ok(())
}

pub fn systemd_notify_stopping() -> Result<(), Error> {
    notify(false, [(STATE_STOPPING, "1")].iter())?;
    Ok(())
}
```

**Systemd Service File** (`{{MODULE_NAME}}.service`):
```ini
[Unit]
Description={{SERVICE_DESCRIPTION}}
After=network.target

[Service]
Type=notify
ExecStart={{INSTALL_PATH}}/{{MODULE_NAME}}
Restart=on-failure
RestartSec=5s
User={{SERVICE_USER}}
Group={{SERVICE_GROUP}}

# Security Hardening
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
NoNewPrivileges=true
ReadWritePaths={{DATA_PATH}}

[Install]
WantedBy=multi-user.target
```

**Reference**: See `references/linux/systemd_service.md` for complete systemd guide.

---

## procfs Access

Read process information from /proc:

```rust
use procfs::process::Process;

pub fn get_process_info(pid: i32) -> Result<ProcessInfo, Error> {
    let process = Process::new(pid)?;

    let stat = process.stat()?;
    let status = process.status()?;

    Ok(ProcessInfo {
        name: stat.comm,
        state: stat.state,
        memory_kb: status.vmrss.unwrap_or(0),
        cpu_time: stat.utime + stat.stime,
    })
}
```

**Reference**: See `references/linux/procfs_access.md` for complete /proc guide.

---

## Related Documentation

- [LINUX_MODULE.md](./LINUX_MODULE.md) - Main index
- [LINUX_MODULE-part2-build-config.md](./LINUX_MODULE-part2-build-config.md) - Build configuration
- [LINUX_MODULE-part4-testing-packaging.md](./LINUX_MODULE-part4-testing-packaging.md) - Testing and packaging
- `references/linux/inotify_api.md` - File system monitoring
- `references/linux/dbus_integration.md` - D-Bus communication
- `references/linux/systemd_service.md` - systemd service creation
- `references/linux/procfs_access.md` - /proc filesystem access
