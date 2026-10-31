"""Regression checks for the deliberately private staging network policy."""
import unittest
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


class PrivateBlogPolicyTests(unittest.TestCase):
    def test_libvirt_state_matching_is_not_disabled(self):
        policy = ElementTree.parse(ROOT / 'deploy/vm/blog-filter.xml')
        state_rules = [rule for rule in policy.findall('rule')
                       if any('state' in child.attrib for child in rule)]
        self.assertTrue(state_rules)
        for rule in state_rules:
            # libvirt drops the state condition when statematch=false, turning
            # an INVALID drop or ESTABLISHED accept into an unconditional rule.
            self.assertNotIn(rule.get('statematch'), ('false', '0'))

    def test_unsolicited_inbound_is_private_ssh_and_http_only(self):
        policy = ElementTree.parse(ROOT / 'deploy/vm/blog-filter.xml')
        ports = set()
        for rule in policy.findall('rule'):
            if rule.get('action') != 'accept' or rule.get('direction') != 'in':
                continue
            tcp = rule.find('tcp')
            if tcp is not None:
                self.assertEqual(tcp.get('srcipaddr'), '192.168.231.1')
                self.assertNotIn('srcipmask', tcp.attrib)
                self.assertNotIn('dstportend', tcp.attrib)
                ports.add(tcp.get('dstportstart'))
            else:
                self.assertIsNotNone(rule.find('mac'))
        self.assertEqual(ports, {'22', '80'})


if __name__ == '__main__':
    unittest.main()
