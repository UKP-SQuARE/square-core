.. SQuARE Docs documentation master file, created by
   sphinx-quickstart on Mon Dec 27 13:03:18 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================================
SQuARE - Software for Question Answering Research
==================================================

.. note::
   To get started directly, please visit the :ref:`get started<Get Started>` page.


SQuARE is a scalable and flexible **open-source** QA platform that enables researchers and developers to:

* Share their custom QA agents by integrating them to our platform using easy-to-use common interfaces.
* Study the strengths and weaknesses of existing models by comparing them on a wide range of tasks and datasets that are already provided within our framework.
* Explore the existing models and datasets to answer more specific research questions using integrated interpretability tools.

.. note::
   Find out more about the project on `UKPs Website <https://www.informatik.tu-darmstadt.de/ukp/research_ukp/ukp_research_projects/ukp_project_square/ukp_project_square_details.en.jsp>`_.

Architecture
-------------

.. figure:: images/square_arch.svg
   :width: 800
   :align: center
   :alt: SQuARE Architecture


.. toctree::
    :caption: Overview
    :maxdepth: 2

    pages/overview/get_started.md
    pages/overview/use_cases.md
    pages/overview/tutorials.md
    pages/overview/roadmap.md
    pages/overview/faq.md

.. toctree::
    :caption: Components
    :maxdepth: 2

    pages/components/datastores.md
    pages/components/models.md
    pages/components/skills.md
    pages/components/explainability.md

.. toctree::
    :caption: API
    :maxdepth: 4

    pages/api/datastore_api/datastores.rst
    pages/api/model_api/models.rst
    pages/api/skill_api/skills.rst
