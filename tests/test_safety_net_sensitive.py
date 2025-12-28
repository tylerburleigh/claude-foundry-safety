"""Tests for sensitive file read blocking."""

from .safety_net_test_base import SafetyNetTestCase


class SensitiveFileBlockedTests(SafetyNetTestCase):
    """Tests for blocked sensitive file reads."""

    # SSH keys
    def test_cat_ssh_dir_blocked(self) -> None:
        self._assert_blocked("cat ~/.ssh/id_rsa", "sensitive files")

    def test_cat_ssh_config_blocked(self) -> None:
        self._assert_blocked("cat ~/.ssh/config", "sensitive files")

    def test_cat_ssh_known_hosts_blocked(self) -> None:
        self._assert_blocked("cat ~/.ssh/known_hosts", "sensitive files")

    # API keys
    def test_cat_api_keys_blocked(self) -> None:
        self._assert_blocked("cat ~/.api_keys", "sensitive files")

    # GitHub CLI
    def test_cat_gh_hosts_blocked(self) -> None:
        self._assert_blocked("cat ~/.config/gh/hosts.yml", "sensitive files")

    # Gemini
    def test_cat_gemini_blocked(self) -> None:
        self._assert_blocked("cat ~/.gemini/config", "sensitive files")

    # OpenCode
    def test_cat_opencode_blocked(self) -> None:
        self._assert_blocked("cat ~/.config/opencode/config.json", "sensitive files")

    # Cursor
    def test_cat_cursor_blocked(self) -> None:
        self._assert_blocked("cat ~/.cursor/config", "sensitive files")

    # Codex
    def test_cat_codex_blocked(self) -> None:
        self._assert_blocked("cat ~/.codex/config", "sensitive files")

    # Git config
    def test_cat_gitconfig_blocked(self) -> None:
        self._assert_blocked("cat ~/.gitconfig", "sensitive files")

    # Claude credentials
    def test_cat_claude_credentials_blocked(self) -> None:
        self._assert_blocked("cat ~/.claude/.credentials.json", "sensitive files")

    def test_cat_claude_config_blocked(self) -> None:
        self._assert_blocked("cat ~/.claude/.claude.json", "sensitive files")


class SensitiveReadCommandsTests(SafetyNetTestCase):
    """Tests for different read commands on sensitive files."""

    def test_less_ssh_blocked(self) -> None:
        self._assert_blocked("less ~/.ssh/id_rsa", "sensitive files")

    def test_more_ssh_blocked(self) -> None:
        self._assert_blocked("more ~/.ssh/id_rsa", "sensitive files")

    def test_head_ssh_blocked(self) -> None:
        self._assert_blocked("head ~/.ssh/id_rsa", "sensitive files")

    def test_tail_ssh_blocked(self) -> None:
        self._assert_blocked("tail ~/.ssh/id_rsa", "sensitive files")

    def test_bat_ssh_blocked(self) -> None:
        self._assert_blocked("bat ~/.ssh/id_rsa", "sensitive files")

    def test_view_ssh_blocked(self) -> None:
        self._assert_blocked("view ~/.ssh/id_rsa", "sensitive files")

    def test_strings_ssh_blocked(self) -> None:
        self._assert_blocked("strings ~/.ssh/id_rsa", "sensitive files")

    def test_xxd_ssh_blocked(self) -> None:
        self._assert_blocked("xxd ~/.ssh/id_rsa", "sensitive files")

    def test_hexdump_ssh_blocked(self) -> None:
        self._assert_blocked("hexdump ~/.ssh/id_rsa", "sensitive files")

    def test_od_ssh_blocked(self) -> None:
        self._assert_blocked("od ~/.ssh/id_rsa", "sensitive files")


class SensitivePathVariantsTests(SafetyNetTestCase):
    """Tests for different path formats."""

    def test_home_var_ssh_blocked(self) -> None:
        self._assert_blocked("cat $HOME/.ssh/id_rsa", "sensitive files")

    def test_home_braces_ssh_blocked(self) -> None:
        self._assert_blocked("cat ${HOME}/.ssh/id_rsa", "sensitive files")

    def test_absolute_home_path_blocked(self) -> None:
        self._assert_blocked("cat /home/tyler/.ssh/id_rsa", "sensitive files")


class SensitiveEmbeddedTests(SafetyNetTestCase):
    """Tests for sensitive reads in embedded commands."""

    def test_bash_c_cat_ssh_blocked(self) -> None:
        self._assert_blocked("bash -c 'cat ~/.ssh/id_rsa'", "sensitive files")

    def test_sh_c_cat_ssh_blocked(self) -> None:
        self._assert_blocked("sh -c 'cat ~/.ssh/id_rsa'", "sensitive files")


class NonSensitiveAllowedTests(SafetyNetTestCase):
    """Tests for allowed non-sensitive file reads."""

    def test_cat_regular_file_allowed(self) -> None:
        self._assert_allowed("cat README.md")

    def test_cat_project_file_allowed(self) -> None:
        self._assert_allowed("cat ./src/main.py")

    def test_cat_home_non_sensitive_allowed(self) -> None:
        self._assert_allowed("cat ~/.bashrc")

    def test_cat_home_profile_allowed(self) -> None:
        self._assert_allowed("cat ~/.profile")

    def test_head_regular_file_allowed(self) -> None:
        self._assert_allowed("head -n 10 file.txt")

    def test_tail_regular_file_allowed(self) -> None:
        self._assert_allowed("tail -f /var/log/syslog")

    def test_less_regular_file_allowed(self) -> None:
        self._assert_allowed("less README.md")

    # Claude settings (not credentials) should be allowed
    def test_cat_claude_settings_allowed(self) -> None:
        self._assert_allowed("cat ~/.claude/settings.json")
