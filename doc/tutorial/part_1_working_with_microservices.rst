.. _tutorial_part1:

*************************************
Scenario: working with micro-services
*************************************

In this scenerio we'll see how Dodo Commands can be used to work with two micro-services. It's definitely over-kill to use Dodo Commmands in this simple scenario, but as the project grows bigger, it will start to be worth it. To keep it simple the services are not Dockerized. The source code for this scenario is found in tutorial/micro_services/before of the `dodo_commands_tutorial <https://github.com/mnieber/dodo_commands_tutorial>` repository.

.. tip::

  In the tutorials we'll assume that Bash is used. In some cases we will source the output of a Dodo command using ``$(dodo <command>)``. If you are using the Fish shell, then you can use ``dodo <command> | source``. In case you are curious what is being sourced, you can run the command without ``$()`` and source it manually on the command line.


Two simple micro-services
=========================

The first micro-service writes the time to a file in the ``/tmp`` directory, whereas the second micro-service runs a ``tail`` command that tracks the contents of this file. We will go ahead and clone the code for this part of the tutorial:

.. code-block:: bash

  cd /tmp
  git clone git@github.com:mnieber/dodo_commands_tutorial.git

  # Copy part 1 of the tutorial so that we can work with a short path
  cp -rf ./dodo_commands_tutorial/part1/before ./dodo_tutorial

Let's try out the services:

.. code-block:: bash

  cd /tmp/dodo_tutorial/writer
  make runserver

  cd /tmp/dodo_tutorial/reader
  make runserver


Setting up an environment
=========================

The next step is to create a Dodo Commands environment for working with our project:

.. code-block:: bash

  cd /tmp/dodo_tutorial
  $(dodo env --init dodo_tutorial)

The environment contains the following directories:

.. code-block:: bash

  # The project dir is where your project lives.
  # In this case, it's the directory where we called 'dodo env --init'.
  dodo which --project-dir

      */tmp/dodo_tutorial*

  # The configuration directory is where the Dodo Commands configuration files
  # for the environment are stored.
  dodo which --config-dir

      /tmp/dodo_tutorial/.dodo_commands

  # The environment directory is where Dodo Commands stores all other information
  # about your environment. Usually, you don't need to work with this directory directly.
  dodo which --env-dir

      ~/.dodo_commands/envs/dodo_tutorial

  # The (optional) python_env directory contains the virtual Python environment for your project.
  # In this case, we don't have any
  dodo which --python-env-dir

      (nothing here)

Working with the configuration
==============================

Each environment contains a set of configuration files:

.. code-block:: bash

  # The main configuration file is called config.yaml
  dodo which --config

      /tmp/dodo_tutorial/.dodo_commands/config.yaml

  # Let's take a look at the configuration file:
  cat $(dodo which --config)

      ROOT:
      command_path:
      - ~/.dodo_commands/default_project/commands/*
      version: 1.0.0

  # When we print the contents of the configuration, we see that some extra values
  # were added automatically
  dodo print-config

      ROOT:
      env_name: dodo_tutorial
      command_path:
      - ~/.dodo_commands/default_project/commands/*
      - /some/path/to/dodo_commands/dodo_system_commands
      project_dir: /tmp/dodo_commands_tutorial/part1
      config_dir: /tmp/dodo_commands_tutorial/part1/.dodo_commands
      version: 1.0.0

You can extend the configuration in any way you like. Let's add the following section:

.. code-block:: yaml

  # (bottom of) /tmp/dodo_tutorial/.dodo_commands/config.yaml
  MAKE:
    cwd: ${/ROOT/project_dir}/writer

Now, when we print the contents of the ``MAKE`` section, we get:

.. code-block:: bash

  dodo print-config MAKE

      cwd: /tmp/dodo_tutorial/writer

We see that we can interpolate values, for example ``${/ROOT/project_dir}``.

.. note::

    From here on, we will use the notation ${/FOO/bar} to refer to the ``bar``
    key in the ``FOO`` section of the configuration file.


Adding an alias to run the writer service
=========================================

We'll now create an alias that runs the writer service.

.. code-block:: bash

  cd /tmp/dodo_tutorial
  mkdir ./commands
  touch ./commands/mk.py

Add the following code to ``mk.py``:

.. code-block:: python

  from dodo_commands import Dodo

  Dodo.parser.add_argument("what")
  Dodo.run(["make", Dodo.args.what], cwd=Dodo.get("/MAKE/cwd"))

We need one last step to ensure that Dodo Commands finds the new command.
Open ``/tmp/dodo_tutorial/.dodo_commands/config.yaml`` again and edit
``${/ROOT/command_path}`` so it looks like this:

.. code-block:: yaml

  ROOT:
    command_path:
    - ~/.dodo_commands/default_project/commands/*
    - ${/ROOT/project_dir}/commands

Now when we run ``dodo`` (without passing any arguments) we get a list of all
available commands, and ``mk`` should be somewhere in that list. To run the
command, let's use the ``--confirm`` flag so we can check that everything is looking good:

.. code-block:: bash

  dodo mk runserver --confirm

      (/tmp/dodo_tutorial/writer) make runserver

      confirm? [Y/n]

We see that the command will run ``make runserver`` in the ``/tmp/dodo_tutorial/writer directory``, great!


Using layers to run the reader and writer service
=================================================

Of course, we made a rather strange choice in our configuration file by binding ${/MAKE/cwd} to the
directory of the writer service. What if we want to run the Makefile of the reader service?
To fix this we will move the ${/MAKE} section to a new configuration file: ``server.writer.yaml``. This
file should therefore look like this:

.. code-block:: yaml

  # /tmp/dodo_tutorial/.dodo_commands/server.writer.yaml
  MAKE:
    cwd: ${/ROOT/project_dir}/writer

Add a similar file for the reader:

.. code-block:: yaml

  # /tmp/dodo_tutorial/.dodo_commands/server.reader.yaml
  MAKE:
    cwd: ${/ROOT/project_dir}/reader

Finally, we will add a ``LAYERS_GROUP`` in the main configuration file:

.. code-block:: yaml

  # (bottom of) /tmp/dodo_tutorial/.dodo_commands/config.yaml
  LAYER_GROUPS:
    server:
    - writer
    - reader

Now when we call ``dodo writer.mk runserver`` then Dodo Commands will look for a layer
that has the name ``writer``. It will find this layer in the ``server`` group and load the
``server.writer.yaml`` layer:

.. code-block:: bash

  dodo writer.mk runserver --confirm

      (/tmp/dodo_tutorial/writer) make runserver

      confirm? [Y/n]

Of course, to run the reader, we can use ``dodo reader.mk runserver``.

.. tip::

  We saw above the Dodo Commands applies some magic to find out what command you want to run. Use
  the ``--trace`` option to print the result of this translation process (without running any commands).
  For example:

  .. code-block:: bash

    dodo reader.mk runserver --trace

        ['/usr/local/bin/dodo', 'mk', 'runserver', '--layer=server.reader.yaml']

  This tells us that we can also invoke this command as ``dodo mk runserver --layer=server.reader.yaml``.


Running the services in tmux
============================

We'll now put the commands to run our services in a menu so we can easily run them
in a tmux session. Add a ``MENU`` section to the configuration file like this:

.. code-block:: yaml

  # (bottom of) /tmp/dodo_tutorial/.dodo_commands/config.yaml
  MENU:
    commands:
      server:
      - dodo writer.mk runserver
      - dodo reader.mk runserver

When we run ``dodo menu --tmux`` we'll open a tmux session that show the menu:

  .. code-block:: bash

    dodo menu --tmux

         1 [server] - dodo writer.mk runserver
         2 [server] - dodo reader.mk runserver

        Select one or more commands (e.g. 1,3-4) or type 0 to exit:

Type ``1,2`` to run both commands. They will open in separate windows inside the tmux screen.