import io
import os
from unittest import mock

import pytest
import uqbar.io
import uqbar.strings
import yaml

import supriya.cli
import supriya.nonrealtime


def test_missing_material(cli_paths):
    """
    Handle missing material.
    """
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info:
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
            No matching materials.
        Available materials:
            No materials available.
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_missing_definition(cli_paths):
    """
    Handle missing definition.
    """
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    material_path = pytest.helpers.create_cli_material(
        cli_paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    definition_path.unlink()
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info:
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
        Traceback (most recent call last):
            File ".../ProjectPackageScript.py", line ..., in _import_path
            return importlib.import_module(path)
            ...
        ModuleNotFoundError: No module named 'test_project.materials.test_material.definition'
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_python_cannot_render(cli_paths):
    """
    Handle un-renderables.
    """
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    material_path = pytest.helpers.create_cli_material(
        cli_paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with definition_path.open("w") as file_pointer:
        file_pointer.write(
            uqbar.strings.normalize(
                r"""
        material = None
        """
            )
        )
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info:
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
            Cannot render material of type NoneType.
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_python_error_on_render(cli_paths):
    """
    Handle exceptions inside the Python module on __call__().
    """
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    material_path = pytest.helpers.create_cli_material(
        cli_paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with definition_path.open("w") as file_pointer:
        file_pointer.write(
            uqbar.strings.normalize(
                r"""
        class Foo:
            def __render__(
                cli_paths,
                output_file_path=None,
                render_directory_path=None,
                **kwargs
                ):
                raise TypeError('This is fake.')

        material = Foo()
        """
            )
        )
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io):
        with uqbar.io.DirectoryChange(cli_paths.inner_project_path):
            with pytest.raises(SystemExit) as exception_info:
                script(command)
            assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
        Traceback (most recent call last):
            File ".../supriya/cli/ProjectSectionScript.py", line ..., in _render_object
            **kwargs,
            File ".../supriya/io.py", line ..., in render
            **kwargs,
            File
            ".../test_project/test_project/materials/test_material/definition.py", line ..., in __render__
            raise TypeError('This is fake.')
        TypeError: This is fake.
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_python_error_on_import(cli_paths):
    """
    Handle exceptions inside the Python module on import.
    """
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    material_path = pytest.helpers.create_cli_material(
        cli_paths.test_directory_path, "test_material"
    )
    definition_path = material_path.joinpath("definition.py")
    with definition_path.open("a") as file_pointer:
        file_pointer.write("\n\nfailure = 1 / 0\n")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info:
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
        Traceback (most recent call last):
            File ".../supriya/cli/ProjectPackageScript.py", line ..., in _import_path
            return importlib.import_module(path)
            ...
            File ".../test_project/test_project/materials/test_material/definition.py", line ..., in <module>
            failure = 1 / 0
        ZeroDivisionError: division by zero
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_supercollider_error(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "test_material")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    mock_path = supriya.nonrealtime.SessionRenderer.__module__
    mock_path += "._stream_subprocess"
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info, mock.patch(mock_path) as call_mock:
        call_mock.return_value = 1
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 1.
                SuperCollider errored!
            Python/SC runtime: 0 seconds
            Render failed. Exiting.
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_supercollider_no_output(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "test_material")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    mock_path = supriya.nonrealtime.SessionRenderer.__module__
    mock_path += "._stream_subprocess"
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ), pytest.raises(SystemExit) as exception_info, mock.patch(mock_path) as call_mock:
        call_mock.return_value = 0  # no output, but no error
        script(command)
    assert exception_info.value.code == 1
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
                Output file is missing!
            Python/SC runtime: 0 seconds
            Render failed. Exiting.
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )


def test_success_all_materials(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_one")
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_two")
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_three")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "*"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ):
        try:
            script(command)
        except SystemExit as e:
            raise RuntimeError("SystemExit: {}".format(e.code))
    pytest.helpers.compare_strings(
        r"""
        Render candidates: '*' ...
        Rendering test_project/materials/material_one/
            Importing test_project.materials.material_one.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/materials/material_one/render.yml.
                Wrote test_project/materials/material_one/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_one/
        Rendering test_project/materials/material_three/
            Importing test_project.materials.material_three.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/materials/material_three/render.yml.
                Wrote test_project/materials/material_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_three/
        Rendering test_project/materials/material_two/
            Importing test_project.materials.material_two.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/materials/material_two/render.yml.
                Wrote test_project/materials/material_two/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_two/
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )
    assert cli_paths.materials_path.joinpath("material_one", "render.aiff").exists()
    assert cli_paths.materials_path.joinpath("material_two", "render.aiff").exists()
    assert cli_paths.materials_path.joinpath("material_three", "render.aiff").exists()
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("material_one", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("material_two", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("material_three", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }


def test_success_filtered_materials(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_one")
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_two")
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_three")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "material_t*"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ):
        try:
            script(command)
        except SystemExit as e:
            raise RuntimeError("SystemExit: {}".format(e.code))
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'material_t*' ...
        Rendering test_project/materials/material_three/
            Importing test_project.materials.material_three.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/materials/material_three/render.yml.
                Wrote test_project/materials/material_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_three/
        Rendering test_project/materials/material_two/
            Importing test_project.materials.material_two.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. File already exists.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Skipped session-95cecb2c724619fe502164459560ba5d.osc. Output already exists.
            Writing test_project/materials/material_two/render.yml.
                Wrote test_project/materials/material_two/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_two/
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )
    assert not cli_paths.materials_path.joinpath("material_one", "render.aiff").exists()
    assert cli_paths.materials_path.joinpath("material_two", "render.aiff").exists()
    assert cli_paths.materials_path.joinpath("material_three", "render.aiff").exists()
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("material_two", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("material_three", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }


def test_success_one_material(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "test_material")
    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "test_material"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ):
        try:
            script(command)
        except SystemExit as e:
            raise RuntimeError("SystemExit: {}".format(e.code))
    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'test_material' ...
        Rendering test_project/materials/test_material/
            Importing test_project.materials.test_material.definition
            Writing session-95cecb2c724619fe502164459560ba5d.osc.
                Wrote session-95cecb2c724619fe502164459560ba5d.osc.
            Rendering session-95cecb2c724619fe502164459560ba5d.osc.
                Command: scsynth -N session-95cecb2c724619fe502164459560ba5d.osc _ session-95cecb2c724619fe502164459560ba5d.aiff 44100 aiff int24
                Rendered session-95cecb2c724619fe502164459560ba5d.osc with exit code 0.
            Writing test_project/materials/test_material/render.yml.
                Wrote test_project/materials/test_material/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/test_material/
        """.replace(
            "/", os.path.sep
        ),
        string_io.getvalue(),
    )
    pytest.helpers.compare_path_contents(
        cli_paths.inner_project_path,
        [
            "test_project/test_project/__init__.py",
            "test_project/test_project/assets/.gitignore",
            "test_project/test_project/distribution/.gitignore",
            "test_project/test_project/etc/.gitignore",
            "test_project/test_project/materials/.gitignore",
            "test_project/test_project/materials/__init__.py",
            "test_project/test_project/materials/test_material/__init__.py",
            "test_project/test_project/materials/test_material/definition.py",
            "test_project/test_project/materials/test_material/render.aiff",
            "test_project/test_project/materials/test_material/render.yml",
            "test_project/test_project/project-settings.yml",
            "test_project/test_project/renders/.gitignore",
            "test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.aiff",
            "test_project/test_project/renders/session-95cecb2c724619fe502164459560ba5d.osc",
            "test_project/test_project/sessions/.gitignore",
            "test_project/test_project/sessions/__init__.py",
            "test_project/test_project/synthdefs/.gitignore",
            "test_project/test_project/synthdefs/__init__.py",
            "test_project/test_project/test/.gitignore",
            "test_project/test_project/tools/.gitignore",
            "test_project/test_project/tools/__init__.py",
        ],
        cli_paths.test_directory_path,
    )
    assert pytest.helpers.sample_soundfile(
        cli_paths.materials_path.joinpath("test_material", "render.aiff")
    ) == {
        0.0: [2.3e-05] * 8,
        0.21: [0.210_295] * 8,
        0.41: [0.410_567] * 8,
        0.61: [0.610_839] * 8,
        0.81: [0.811_111] * 8,
        0.99: [0.991_361] * 8,
    }


def test_success_chained(cli_paths):
    string_io = io.StringIO()
    pytest.helpers.create_cli_project(cli_paths.test_directory_path)
    pytest.helpers.create_cli_material(cli_paths.test_directory_path, "material_one")
    pytest.helpers.create_cli_material(
        cli_paths.test_directory_path,
        "material_two",
        definition_contents=pytest.helpers.get_chained_session_template().render(
            input_name="material_one",
            input_section_singular="material",
            output_section_singular="material",
            multiplier=0.5,
        ),
    )
    material_three_path = pytest.helpers.create_cli_material(
        cli_paths.test_directory_path,
        "material_three",
        definition_contents=pytest.helpers.get_chained_session_template().render(
            input_name="material_two",
            input_section_singular="material",
            output_section_singular="material",
            multiplier=-1.0,
        ),
    )

    project_settings_path = cli_paths.inner_project_path / "project-settings.yml"
    with project_settings_path.open() as file_pointer:
        project_settings = file_pointer.read()
    project_settings = project_settings.replace(
        "input_bus_channel_count: 8", "input_bus_channel_count: 2"
    )
    project_settings = project_settings.replace(
        "output_bus_channel_count: 8", "output_bus_channel_count: 2"
    )
    with project_settings_path.open("w") as file_pointer:
        file_pointer.write(project_settings)

    pytest.helpers.compare_path_contents(
        cli_paths.inner_project_path,
        [
            "test_project/test_project/__init__.py",
            "test_project/test_project/assets/.gitignore",
            "test_project/test_project/distribution/.gitignore",
            "test_project/test_project/etc/.gitignore",
            "test_project/test_project/materials/.gitignore",
            "test_project/test_project/materials/__init__.py",
            "test_project/test_project/materials/material_one/__init__.py",
            "test_project/test_project/materials/material_one/definition.py",
            "test_project/test_project/materials/material_three/__init__.py",
            "test_project/test_project/materials/material_three/definition.py",
            "test_project/test_project/materials/material_two/__init__.py",
            "test_project/test_project/materials/material_two/definition.py",
            "test_project/test_project/project-settings.yml",
            "test_project/test_project/renders/.gitignore",
            "test_project/test_project/sessions/.gitignore",
            "test_project/test_project/sessions/__init__.py",
            "test_project/test_project/synthdefs/.gitignore",
            "test_project/test_project/synthdefs/__init__.py",
            "test_project/test_project/test/.gitignore",
            "test_project/test_project/tools/.gitignore",
            "test_project/test_project/tools/__init__.py",
        ],
        cli_paths.test_directory_path,
    )

    script = supriya.cli.ManageMaterialScript()
    command = ["--render", "material_three"]
    with uqbar.io.RedirectedStreams(stdout=string_io), uqbar.io.DirectoryChange(
        cli_paths.inner_project_path
    ):
        try:
            script(command)
        except SystemExit as e:
            raise RuntimeError("SystemExit: {}".format(e.code))

    pytest.helpers.compare_strings(
        r"""
        Render candidates: 'material_three' ...
        Rendering test_project/materials/material_three/
            Importing test_project.materials.material_three.definition
            Writing session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
                Wrote session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
            Rendering session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc.
                Command: scsynth -N session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc _ session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc with exit code 0.
            Writing session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
                Wrote session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
            Rendering session-46f9bdbbd13bcf641e2a79917dcc041f.osc.
                Command: scsynth -N session-46f9bdbbd13bcf641e2a79917dcc041f.osc session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff session-46f9bdbbd13bcf641e2a79917dcc041f.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-46f9bdbbd13bcf641e2a79917dcc041f.osc with exit code 0.
            Writing session-352b87b6c1d447a5be11020a33ceadec.osc.
                Wrote session-352b87b6c1d447a5be11020a33ceadec.osc.
            Rendering session-352b87b6c1d447a5be11020a33ceadec.osc.
                Command: scsynth -N session-352b87b6c1d447a5be11020a33ceadec.osc session-46f9bdbbd13bcf641e2a79917dcc041f.aiff session-352b87b6c1d447a5be11020a33ceadec.aiff 44100 aiff int24 -i 2 -o 2
                Rendered session-352b87b6c1d447a5be11020a33ceadec.osc with exit code 0.
            Writing test_project/materials/material_three/render.yml.
                Wrote test_project/materials/material_three/render.yml.
            Python/SC runtime: 0 seconds
            Rendered test_project/materials/material_three/
        """,
        string_io.getvalue(),
    )

    pytest.helpers.compare_path_contents(
        cli_paths.inner_project_path,
        [
            "test_project/test_project/__init__.py",
            "test_project/test_project/assets/.gitignore",
            "test_project/test_project/distribution/.gitignore",
            "test_project/test_project/etc/.gitignore",
            "test_project/test_project/materials/.gitignore",
            "test_project/test_project/materials/__init__.py",
            "test_project/test_project/materials/material_one/__init__.py",
            "test_project/test_project/materials/material_one/definition.py",
            "test_project/test_project/materials/material_three/__init__.py",
            "test_project/test_project/materials/material_three/definition.py",
            "test_project/test_project/materials/material_three/render.aiff",
            "test_project/test_project/materials/material_three/render.yml",
            "test_project/test_project/materials/material_two/__init__.py",
            "test_project/test_project/materials/material_two/definition.py",
            "test_project/test_project/project-settings.yml",
            "test_project/test_project/renders/.gitignore",
            "test_project/test_project/renders/session-352b87b6c1d447a5be11020a33ceadec.aiff",
            "test_project/test_project/renders/session-352b87b6c1d447a5be11020a33ceadec.osc",
            "test_project/test_project/renders/session-46f9bdbbd13bcf641e2a79917dcc041f.aiff",
            "test_project/test_project/renders/session-46f9bdbbd13bcf641e2a79917dcc041f.osc",
            "test_project/test_project/renders/session-aa1ca9fda49a2dd38a1a2b8a91a76cca.aiff",
            "test_project/test_project/renders/session-aa1ca9fda49a2dd38a1a2b8a91a76cca.osc",
            "test_project/test_project/sessions/.gitignore",
            "test_project/test_project/sessions/__init__.py",
            "test_project/test_project/synthdefs/.gitignore",
            "test_project/test_project/synthdefs/__init__.py",
            "test_project/test_project/test/.gitignore",
            "test_project/test_project/tools/.gitignore",
            "test_project/test_project/tools/__init__.py",
        ],
        cli_paths.test_directory_path,
    )

    render_yml_file_path = material_three_path / "render.yml"
    with render_yml_file_path.open() as file_pointer:
        render_yml = yaml.load(file_pointer.read())
    assert render_yml == {
        "render": "session-352b87b6c1d447a5be11020a33ceadec",
        "source": [
            "session-46f9bdbbd13bcf641e2a79917dcc041f",
            "session-aa1ca9fda49a2dd38a1a2b8a91a76cca",
        ],
    }

    material_three_render_sample = pytest.helpers.sample_soundfile(
        material_three_path / "render.aiff", rounding=2
    )

    material_three_source_sample = pytest.helpers.sample_soundfile(
        cli_paths.renders_path / "{}.aiff".format(render_yml["render"]), rounding=2
    )

    assert material_three_render_sample == material_three_source_sample
    assert material_three_render_sample == {
        0.0: [-0.0, -0.0],
        0.21: [-0.11, -0.11],
        0.41: [-0.21, -0.21],
        0.61: [-0.31, -0.31],
        0.81: [-0.41, -0.41],
        0.99: [-0.5, -0.5],
    }
