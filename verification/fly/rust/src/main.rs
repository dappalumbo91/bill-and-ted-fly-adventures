//! Fly spine host replay. Pin AEB2AD. Law S = K(T1+T2+T3). 0 free parameters.

mod catalog;

fn main() {
    let phi = (1.0_f64 + 5.0_f64.sqrt()) / 2.0;
    let inv_phi = 1.0 / phi;
    assert!((phi - 1.618033988749895).abs() < 1e-12);
    assert!((inv_phi - 0.618033988749895).abs() < 1e-12);
    catalog::check();
    println!("FSOT_FLY_SPINE_RUST_OK");
    println!("phi={phi:.15}");
    println!("inv_phi={inv_phi:.15}");
}
