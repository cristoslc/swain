//! Broker discovery — parallel TLS handshake to find working MQTT broker.
//!
//! Uses std::thread::scope for parallel connections (no async runtime needed).
//! Used by `hcom relay new` to find and pin the fastest public broker.

use std::net::{TcpStream, ToSocketAddrs};
use std::sync::Arc;
use std::time::{Duration, Instant};

/// Result of testing a single broker: (host, port, ping_ms or None on failure).
pub type BrokerTestResult = (String, u16, Option<u64>);

/// Test a single broker via TCP+TLS handshake. Returns round-trip ms or None.
pub fn ping_broker(host: &str, port: u16, use_tls: bool) -> Option<u64> {
    let t0 = Instant::now();
    let socket_addr = format!("{}:{}", host, port)
        .to_socket_addrs()
        .ok()?
        .next()?;
    let mut stream = TcpStream::connect_timeout(&socket_addr, Duration::from_secs(5)).ok()?;

    if use_tls {
        // TCP+TLS handshake only. Verify the broker is reachable and accepts TLS.
        // Set timeouts so handshake doesn't block forever on unreachable brokers.
        stream.set_read_timeout(Some(Duration::from_secs(5))).ok()?;
        stream
            .set_write_timeout(Some(Duration::from_secs(5)))
            .ok()?;

        let mut root_store = rustls::RootCertStore::empty();
        root_store.extend(webpki_roots::TLS_SERVER_ROOTS.iter().cloned());
        let config = rustls::ClientConfig::builder()
            .with_root_certificates(root_store)
            .with_no_client_auth();
        let server_name: rustls::pki_types::ServerName<'static> =
            host.to_string().try_into().ok()?;
        let mut conn = rustls::ClientConnection::new(Arc::new(config), server_name).ok()?;

        // Drive TLS handshake via complete_io (handles read/write round-trips).
        // Stops after handshake — the read timeout prevents blocking on post-handshake
        // app data (MQTT brokers wait for CONNECT before sending anything).
        match conn.complete_io(&mut stream) {
            Ok(_) => {}
            Err(_) => {
                // complete_io may error with read timeout after handshake completes
                // (MQTT brokers send no app data until CONNECT). That's OK.
                if conn.is_handshaking() {
                    return None; // Failed during handshake = broker unreachable
                }
            }
        }
    }

    Some(t0.elapsed().as_millis() as u64)
}

/// Test all brokers in parallel. Returns results in input order.
/// Uses std::thread::scope for scoped threads (no Arc needed for shared refs).
pub fn test_brokers_parallel(brokers: &[(&str, u16)]) -> Vec<BrokerTestResult> {
    let mut results: Vec<BrokerTestResult> = brokers
        .iter()
        .map(|(h, p)| (h.to_string(), *p, None))
        .collect();

    std::thread::scope(|s| {
        let handles: Vec<_> = brokers
            .iter()
            .enumerate()
            .map(|(i, (host, port))| {
                let host = host.to_string();
                let port = *port;
                s.spawn(move || {
                    let use_tls = port == 8883 || port == 8886;
                    let ping_ms = ping_broker(&host, port, use_tls);
                    (i, ping_ms)
                })
            })
            .collect();

        for handle in handles {
            if let Ok((i, ping_ms)) = handle.join() {
                results[i].2 = ping_ms;
            }
        }
    });

    results
}

/// Find the first working broker from DEFAULT_BROKERS.
/// Returns (host, port, ping_ms) or None if all unreachable.
pub fn find_working_broker() -> Option<(String, u16, u64)> {
    let results = test_brokers_parallel(super::DEFAULT_BROKERS);
    // Return first reachable broker (preserves priority order)
    results
        .into_iter()
        .find(|(_, _, ping)| ping.is_some())
        .map(|(h, p, ping)| (h, p, ping.unwrap()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_test_brokers_parallel_empty() {
        let results = test_brokers_parallel(&[]);
        assert!(results.is_empty());
    }

    #[test]
    fn test_ping_broker_unreachable() {
        // Non-routable address should fail (timeout ~5s)
        let result = ping_broker("192.0.2.1", 8883, true);
        assert!(result.is_none());
    }

    #[test]
    fn test_test_brokers_parallel_unreachable() {
        let brokers = &[("192.0.2.1", 8883), ("192.0.2.2", 8883)];
        let results = test_brokers_parallel(brokers);
        assert_eq!(results.len(), 2);
        assert!(results[0].2.is_none());
        assert!(results[1].2.is_none());
    }
}
