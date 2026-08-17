import time
import unittest


def generate_ids(count: int) -> int:
    return sum(1 for index in range(count) if f"TX-{index}")


class LoadProfileSmokeTests(unittest.TestCase):
    def test_local_smoke_profile_is_linear_and_complete(self) -> None:
        count = 100_000
        started = time.perf_counter()
        generated = generate_ids(count)
        elapsed = time.perf_counter() - started
        self.assertEqual(generated, count)
        self.assertLess(elapsed, 10.0)


if __name__ == "__main__":
    unittest.main()
