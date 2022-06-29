# The MIT License (MIT)
# Copyright (c) 2022 Gamejam.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial
# portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import click
from blockchainetl_common.logging_utils import logging_basic_config
from solanaetl.jobs.export_blocks_job import ExportBlocksJob
from solanaetl.jobs.exporters.blocks_and_transactions_item_exporter import \
    blocks_and_transactions_item_exporter
from solanaetl.providers.auto import get_provider_from_uri
from solanaetl.thread_local_proxy import ThreadLocalProxy

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, show_default=True, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=1, show_default=True, type=int, help='The number of blocks to export at a time.')
@click.option('-p', '--provider-uri', default='https://api.mainnet-beta.solana.com', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'https://api.mainnet-beta.solana.com')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('--blocks-output', default=None, show_default=True, type=str,
              help='The output file for blocks. If not provided blocks will not be exported. Use "-" for stdout')
@click.option('--transactions-output', default=None, show_default=True, type=str,
              help='The output file for transactions. '
                   'If not provided transactions will not be exported. Use "-" for stdout.')
@click.option('--instructions-output', default=None, show_default=True, type=str,
              help='The output file for instructions. '
                   'If not provided instructions will not be exported. Use "-" for stdout.')
def export_blocks_and_transactions(start_block, end_block, batch_size, provider_uri, max_workers, blocks_output,
                                   transactions_output, instructions_output):
    """Exports blocks and transactions."""
    if blocks_output is None and transactions_output is None:
        raise ValueError(
            'Either --blocks-output or --transactions-output options must be provided')

    if transactions_output is None and instructions_output is not None:
        raise ValueError('--transactions-output options must be provided')

    job = ExportBlocksJob(
        start_block=start_block,
        end_block=end_block,
        batch_size=batch_size,
        batch_web3_provider=ThreadLocalProxy(
            lambda: get_provider_from_uri(provider_uri, batch=True)),
        max_workers=max_workers,
        item_exporter=blocks_and_transactions_item_exporter(
            blocks_output, transactions_output, instructions_output),
        export_blocks=blocks_output is not None,
        export_transactions=transactions_output is not None,
        export_instructions=instructions_output is not None)

    job.run()
