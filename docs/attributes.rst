Attributes
==========

A tag can have a number of attributes, stored in the AST with the following classes.

.. autoclass:: html_renderer.attributes.Attribute
   :show-inheritance:
   :members:
   :undoc-members:

   .. method:: __bool__(self) -> bool

      Converts the attribute to a boolean

   .. method:: __repr__(self) -> str

      Produces a debug string form of the attribute in the format ``f'{ClassName}(\'abs(self)\')'``

   .. method:: __str__(self) -> str

      Converts the attribute to a string, for inserting into a tag

   .. method:: __eq__(self, other: Union[str, Attribute]) -> bool

      Checks to see if the attribute is equal to the `other` parameter.

      * If ``other`` is a string, checks it against the value of the attribute.
      * If ``other`` is an Attribute, checks both type and value.

   .. method:: __ne__(self, other: Union[str, Attribute]) -> bool

      Checks t see if the attribute is not equal to the `other` parameter.

      * If ``other`` is a string, checks it against the value of the attribute.
      * If ``other`` is an Attribute, checks both type and value.

   .. method:: __abs__(self) -> str
      
      Returns the value of the attribute as a string, should be overriden rather than ``__str__`` and ``__repr__``.

.. autoclass:: html_renderer.attributes.Attributes
   :show-inheritance:
   :members:
   :undoc-members:

   .. method:: __add__(self, other: Union[Class]) -> Attributes

      If ``other`` is an instance of `Class <#html_renderer.attributes.class_.Class>`_,
      return a new ``Attributes`` object with the class added.

   .. method:: __iadd__(self, other: Union[Class]) -> Attributes

      * If ``other`` is an instance of `Class <#html_renderer.attributes.class_.Class>`_, add it's value to our classes.
      * If ``other`` is an instance of `Id <#html_renderer.attributes.id.Id>`_, set ``self.id`` to ``other.value``.
      * If ``other`` is an instance of `Attribute <#html_renderer.attributes.Attribute>`_, try to add it's value to the attribute of the same type on ourself, otherwise set our attribute of the same type to ``other``.

   .. method:: __iter__(self) -> Iterable

      Returns an generator of the attributes on the object


.. autoclass:: html_renderer.attributes.class_.Class
   :show-inheritance:
   :members:
   :undoc-members:

.. autoclass:: html_renderer.attributes.id.Id
   :show-inheritance:
   :members:
   :undoc-members:
