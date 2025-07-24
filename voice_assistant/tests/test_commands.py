"""
Tests for command handlers.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
from pathlib import Path

from voice_assistant.commands.base import CommandRegistry
from voice_assistant.commands.browser_commands import BrowserCommand
from voice_assistant.commands.application_commands import ApplicationCommand
from voice_assistant.commands.utility_commands import UtilityCommand
from voice_assistant.config.settings import ConfigManager, Configuration
from voice_assistant.core.exceptions import CommandExecutionError, ApplicationLaunchError


class TestCommandRegistry:
    """Test CommandRegistry class."""
    
    def test_register_command(self):
        """Test registering a command handler."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.__class__.__name__ = "MockCommand"
        
        registry.register(mock_command)
        assert mock_command in registry._commands
    
    def test_unregister_command(self):
        """Test unregistering a command handler."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.__class__.__name__ = "MockCommand"
        
        registry.register(mock_command)
        registry.unregister(mock_command)
        assert mock_command not in registry._commands
    
    def test_get_handler(self):
        """Test getting appropriate command handler."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.can_handle.return_value = True
        
        registry.register(mock_command)
        handler = registry.get_handler("test command")
        
        assert handler == mock_command
        mock_command.can_handle.assert_called_with("test command")
    
    def test_get_handler_not_found(self):
        """Test getting handler when none can handle the command."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.can_handle.return_value = False
        
        registry.register(mock_command)
        handler = registry.get_handler("test command")
        
        assert handler is None
    
    def test_execute_command_success(self):
        """Test successful command execution."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.can_handle.return_value = True
        mock_command.execute.return_value = "success"
        
        registry.register(mock_command)
        result = registry.execute_command("test command")
        
        assert result == "success"
        mock_command.execute.assert_called_with("test command", None)
    
    def test_execute_command_no_handler(self):
        """Test command execution when no handler found."""
        registry = CommandRegistry()
        
        with pytest.raises(CommandExecutionError, match="No handler found for command"):
            registry.execute_command("test command")
    
    def test_list_commands(self):
        """Test listing all registered commands."""
        registry = CommandRegistry()
        mock_command = Mock()
        mock_command.__class__.__name__ = "MockCommand"
        mock_command.command_patterns = ["pattern1", "pattern2"]
        mock_command.description = "Test command"
        
        registry.register(mock_command)
        commands = registry.list_commands()
        
        assert "MockCommand" in commands
        assert commands["MockCommand"]["patterns"] == ["pattern1", "pattern2"]
        assert commands["MockCommand"]["description"] == "Test command"


class TestBrowserCommand:
    """Test BrowserCommand class."""
    
    def test_can_handle_youtube(self):
        """Test handling YouTube command."""
        command = BrowserCommand()
        assert command.can_handle("buka youtube")
        assert command.can_handle("BUKA YOUTUBE")
        assert not command.can_handle("invalid command")
    
    def test_can_handle_google_search(self):
        """Test handling Google search command."""
        command = BrowserCommand()
        assert command.can_handle("cari di google test")
        assert not command.can_handle("invalid command")
    
    def test_can_handle_website(self):
        """Test handling website command."""
        command = BrowserCommand()
        assert command.can_handle("buka website github")
        assert not command.can_handle("invalid command")
    
    @patch('webbrowser.open')
    def test_open_youtube(self, mock_open):
        """Test opening YouTube."""
        command = BrowserCommand()
        result = command.execute("buka youtube")
        
        mock_open.assert_called_with("https://youtube.com")
        assert result == "YouTube opened"
    
    @patch('webbrowser.open')
    def test_search_google(self, mock_open):
        """Test Google search."""
        command = BrowserCommand()
        result = command.execute("cari di google python tutorial")
        
        mock_open.assert_called_with("https://www.google.com/search?q=python+tutorial")
        assert "python tutorial" in result
    
    @patch('webbrowser.open')
    def test_open_website_known(self, mock_open):
        """Test opening known website."""
        command = BrowserCommand()
        result = command.execute("buka website github")
        
        mock_open.assert_called_with("https://github.com")
        assert "https://github.com" in result
    
    @patch('webbrowser.open')
    def test_open_website_unknown(self, mock_open):
        """Test opening unknown website."""
        command = BrowserCommand()
        result = command.execute("buka website unknown")
        
        mock_open.assert_called_with("https://unknown.com")
        assert "https://unknown.com" in result
    
    def test_add_website_shortcut(self):
        """Test adding website shortcut."""
        command = BrowserCommand()
        command.add_website_shortcut("test", "test.com")
        
        assert command.website_shortcuts["test"] == "https://test.com"
    
    def test_remove_website_shortcut(self):
        """Test removing website shortcut."""
        command = BrowserCommand()
        command.add_website_shortcut("test", "test.com")
        command.remove_website_shortcut("test")
        
        assert "test" not in command.website_shortcuts


class TestApplicationCommand:
    """Test ApplicationCommand class."""
    
    def setup_method(self):
        """Setup for each test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = Configuration()
            config.save_to_file(str(config_path))
            
            self.config_manager = ConfigManager(str(config_path))
            self.command = ApplicationCommand(self.config_manager)
    
    def test_can_handle(self):
        """Test command handling detection."""
        assert self.command.can_handle("jalankan aplikasi notepad")
        assert not self.command.can_handle("invalid command")
    
    @patch('subprocess.Popen')
    def test_launch_application_success(self, mock_popen):
        """Test successful application launch."""
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process
        
        result = self.command.execute("jalankan aplikasi notepad")
        
        mock_popen.assert_called_once()
        assert "notepad" in result
    
    @patch('subprocess.Popen')
    def test_launch_application_failure(self, mock_popen):
        """Test application launch failure."""
        mock_popen.side_effect = FileNotFoundError()
        
        with pytest.raises(ApplicationLaunchError):
            self.command.execute("jalankan aplikasi nonexistent")
    
    def test_get_executable_name_default(self):
        """Test getting executable name from defaults."""
        executable = self.command._get_executable_name("notepad")
        assert executable == "notepad.exe"
    
    def test_get_executable_name_variations(self):
        """Test getting executable name with variations."""
        executable = self.command._get_executable_name("vs code")
        assert executable == "code"
    
    def test_add_application_shortcut(self):
        """Test adding application shortcut."""
        self.command.add_application_shortcut("test", "test.exe")
        
        shortcuts = self.command.config_manager.config.application_shortcuts
        assert shortcuts["test"] == "test.exe"
    
    def test_list_application_shortcuts(self):
        """Test listing application shortcuts."""
        shortcuts = self.command.list_application_shortcuts()
        
        # Should include both config shortcuts and default apps
        assert "notepad" in shortcuts
        assert shortcuts["notepad"] == "notepad.exe"


class TestUtilityCommand:
    """Test UtilityCommand class."""
    
    def setup_method(self):
        """Setup for each test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "test_config.json"
            config = Configuration()
            config.save_to_file(str(config_path))
            
            self.config_manager = ConfigManager(str(config_path))
            self.command = UtilityCommand(self.config_manager)
    
    def test_can_handle(self):
        """Test command handling detection."""
        assert self.command.can_handle("ambil screenshot")
        assert self.command.can_handle("screenshot")
        assert self.command.can_handle("tangkap layar")
        assert not self.command.can_handle("invalid command")
    
    @patch('pyautogui.screenshot')
    def test_take_screenshot_success(self, mock_screenshot):
        """Test successful screenshot."""
        # Mock screenshot object with save method
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Update config to use temp directory
            self.config_manager.config.settings.screenshots_folder = temp_dir
            
            result = self.command.execute("ambil screenshot")
            
            mock_screenshot.assert_called_once()
            mock_image.save.assert_called_once()
            assert "Screenshot saved" in result
    
    @patch('pyautogui.size')
    def test_get_screen_info(self, mock_size):
        """Test getting screen information."""
        mock_size.return_value = Mock(width=1920, height=1080)
        
        info = self.command.get_screen_info()
        
        assert info['width'] == 1920
        assert info['height'] == 1080
        assert info['total_pixels'] == 1920 * 1080
    
    def test_list_screenshots_empty(self):
        """Test listing screenshots when none exist."""
        screenshots = self.command.list_screenshots()
        assert screenshots == []
    
    @patch('pyautogui.screenshot')
    def test_cleanup_old_screenshots(self, mock_screenshot):
        """Test cleaning up old screenshots."""
        mock_image = Mock()
        mock_screenshot.return_value = mock_image
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config_manager.config.settings.screenshots_folder = temp_dir
            
            result = self.command.cleanup_old_screenshots(days_old=0)
            assert "0 old screenshots" in result