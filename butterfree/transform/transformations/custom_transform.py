"""CustomTransform entity."""

from typing import Any, Callable, List

from pyspark.sql import DataFrame

from butterfree.transform.transformations.transform_component import TransformComponent


class CustomTransform(TransformComponent):
    """Defines a Custom Transform.

    Attributes:
        transformer: function to use for transforming the dataframe
        **kwargs: kwargs for the transformer

    Example:
        It's necessary to instantiate the CustomTransform class using
        a custom method that must always receive a dataframe and the
        parent feature as arguments and the custom arguments must be
        passed to the builder through *kwargs.

        >>> from butterfree.transform.transformations import CustomTransform
        >>> from butterfree.transform.features import Feature
        >>> from butterfree.constants import DataType
        >>> from pyspark import SparkContext
        >>> from pyspark.sql import session
        >>> import pyspark.sql.functions as F
        >>> sc = SparkContext.getOrCreate()
        >>> spark = session.SparkSession(sc)
        >>> df = spark.createDataFrame([(1, "2016-04-11 11:31:11", 200, 200),
        ...                             (1, "2016-04-11 11:44:12", 300, 300),
        ...                             (1, "2016-04-11 11:46:24", 400, 400),
        ...                             (1, "2016-04-11 12:03:21", 500, 500)]
        ...                           ).toDF("id", "timestamp", "feature1", "feature2")
        >>> def divide(df, parent_feature, column1, column2):
        ...     name = parent_feature.get_output_columns()[0]
        ...     df = df.withColumn(name, F.col(column1) / F.col(column2))
        ...     return df
        >>> feature = Feature(
        ...    name="feature",
        ...    description="custom transform usage example",
        ...    dtype=DataType.DOUBLE,
        ...    transformation=CustomTransform(
        ...        transformer=divide, column1="feature1", column2="feature2",
        ...    )
        ...)
        >>> feature.transform(df).orderBy("timestamp").show()
        +--------+--------+---+-------------------+--------+
        |feature1|feature2| id|          timestamp|feature|
        +--------+--------+---+-------------------+--------+
        |     200|     200|  1|2016-04-11 11:31:11|    1.0|
        |     300|     300|  1|2016-04-11 11:44:12|    1.0|
        |     400|     400|  1|2016-04-11 11:46:24|    1.0|
        |     500|     500|  1|2016-04-11 12:03:21|    1.0|
        +--------+--------+---+-------------------+--------+

    """

    def __init__(self, transformer: Callable[..., Any], **kwargs: Any):
        super().__init__()
        self.transformer = transformer
        self.transformer__kwargs = kwargs

    @property
    def transformer(self) -> Callable[..., Any]:
        """Function to use for transforming the dataframe."""
        return self._transformer

    @transformer.setter
    def transformer(self, method: Callable[..., Any]) -> None:
        if method is None:
            raise ValueError("A method must be provided to CustomTransform")
        self._transformer = method

    @property
    def output_columns(self) -> List[str]:
        """Columns generated by transformation."""
        return [self._parent.name]

    def transform(self, dataframe: DataFrame) -> DataFrame:
        """Performs a transformation to the feature pipeline.

        Args:
            dataframe: input dataframe to be transformed.

        Returns:
            Transformed dataframe.

        """
        dataframe = self.transformer(
            dataframe,
            self.parent,
            **self.transformer__kwargs,
        )
        return dataframe
