Attributes
==========

A tag can have a number of attributes, stored in the AST with the following classes.


Attribute
---------

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

   .. _Attribute EQ

   .. method:: __eq__(self, other: Union[str, Attribute]) -> bool

      Checks to see if the attribute is equal to the `other` parameter.

      * If ``other`` is a string, checks it against the value of the attribute.
      * If ``other`` is an Attribute, checks both type and value.

   .. _Attribute NE

   .. method:: __ne__(self, other: Union[str, Attribute]) -> bool

      Checks t see if the attribute is not equal to the `other` parameter.

      * If ``other`` is a string, checks it against the value of the attribute.
      * If ``other`` is an Attribute, checks both type and value.

   .. method:: __abs__(self) -> str
      
      Returns the value of the attribute as a string, should be overriden rather than ``__str__`` and ``__repr__``.


Attributes
----------

.. autoclass:: html_renderer.attributes.Attributes
   :show-inheritance:
   :members:
   :undoc-members:

   .. method:: __add__(self, other: Union[Class]) -> Attributes

      If ``other`` is an instance of `Class <#html_renderer.attributes.class_.Class>`_,
      return a new ``Attributes`` object with the class added.

   .. method:: __iadd__(self, other: Union[Class]) -> Attributes

      * If ``other`` is an instance of `Class <#html_renderer.attributes.class_.Class>`_, add its value to our classes.
      * If ``other`` is an instance of `Id <#html_renderer.attributes.id.Id>`_, set ``self.id`` to ``other.value``.
      * If ``other`` is an instance of `Attribute <#html_renderer.attributes.Attribute>`_, try to add its value to the attribute of the same type on ourself, otherwise set our attribute of the same type to ``other``.

   .. method:: __iter__(self) -> Iterable

      Returns an generator of the attributes on the object


Class
-----

.. autoclass:: html_renderer.attributes.class_.Class
   :show-inheritance:
   :members:
   :undoc-members:

   .. method:: __add__(self, other: Union[str, Iterable[str], Class]) -> Class

      Returns a new ``Class`` with our values and the values of ``other``

   .. method:: __iadd__(self, other: Union[str, Iterable[str], Class]) -> Class

      * If ``other`` is an instance of ``str``, splits ``other`` by spaces and adds to ``self.value``
      * If ``other`` is an instance of ``Iterable``, adds ``other`` to ``self.value``
      * If ``other`` is an instance of ``Class``, combine ``self.value`` and ``other.value``

   .. method:: __abs__(self) -> str
      
      Returns the value of the class, joined by spaces.

   .. method:: __iter__(self) -> Iterable[str]

      Returns an iterable over the classes

   .. method:: __next__(self) -> str

      Returns the next class of the iterator

   .. method:: __len__(self) -> Iterable[str]

      Returns the number of classes the attribute is holding

   .. method:: __eq__(self, other: Union[str, Iterable[str], Attribute]) -> bool

      * If ``other`` is an instance of ``string``, splits ``other`` by spaces, converts the list to a set and compares it to ``self.value``
      * If ``other`` is an instance of ``Iterable``,  converts ``other`` to a set and compares it to ``self.value``
      * If ``other`` is an instance of ``Class``, compares ``self.value`` to ``other.value``
      * Defaults to :ref:`Attribute EQ`

   .. method:: __ne__(self, other: Union[str, Iterable[str], Attribute]) -> bool

      * If ``other`` is an instance of ``string``, splits ``other`` by spaces, converts the list to a set and compares it to ``self.value``
      * If ``other`` is an instance of ``Iterable``,  converts ``other`` to a set and compares it to ``self.value``
      * If ``other`` is an instance of ``Class``, compares ``self.value`` to ``other.value``
      * Defaults to :ref:`Attribute NE`


   ..
      def __contains__(self, other: Union[str, Iterable[str], Class]) -> bool:
         if isinstance(other, str): return other in self.value
         if isinstance(other, Iterable): return len(self.value & set(other)) > 0
         if isinstance(other, Class): return other.value in self
         return NotImplemented

      def __selector__(self) -> str:
         return ''.join(f'.{c}' for c in self.value)


Id
--

.. autoclass:: html_renderer.attributes.id.Id
   :show-inheritance:
   :members:
   :undoc-members:
