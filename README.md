# spac3
Use spac3 to manage descriptions of attributes in an OpenAPI document. space3 reads an OpenAPI spec and extracts all the descriptions into an MS Excel file. Your product management and technical writing teams can then work on adding descriptions to the attributes in MS Excel. Once the descriptions are added, they can merge the MS Excel file with the original OpenAPI spec document so that the descriptions in the OpenAPI document are updated with the descriptions from the Excel file.

Works with OpenAPI documents in both yaml and json formats.

## See it in action
A hosted version is available at [spac3s.streamlit.app](https://spac3s.streamlit.app).

To run it locally
1. install pre-reqs - python
2. clone the repository
3. install dependancies `pip install requirements.txt -r` from project root
4. run `streamlit run Home.py`


## OpenAPI specifications currently supported
3.1

## Contributing
the usual. iykyk.

## Bonus
additional highly opinionated Overlay processor for modifying OpenAPI docs using an Overlay specification file.