.PHONY: test smoke install clean check fmt

test:
	cargo test

smoke:
	cargo test -- --ignored

install:
	cargo build --release
	install -m 755 target/release/agentrc ~/.cargo/bin/agentrc
	agentrc install

clean:
	cargo clean

check:
	cargo clippy -- -D warnings
	cargo fmt -- --check

fmt:
	cargo fmt
