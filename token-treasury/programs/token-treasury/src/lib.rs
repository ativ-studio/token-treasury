use anchor_lang::prelude::*;
use anchor_lang::solana_program::{
    program_memory::sol_memcmp,
    program_pack::{IsInitialized, Pack},
    pubkey::{Pubkey, PUBKEY_BYTES},
};
use anchor_spl::{
    associated_token::AssociatedToken,
    token::{transfer_checked, Mint, Token, TokenAccount, TransferChecked},
};

declare_id!("GU1B8EVCww9jiAGu7jE4YaEnYa6W1edB7KG3oprVgPyu");

pub fn cmp_pubkeys(a: &Pubkey, b: &Pubkey) -> bool {
    sol_memcmp(a.as_ref(), b.as_ref(), PUBKEY_BYTES) == 0
}

#[error_code]
pub enum TreasuryError {
    #[msg("Account does not have correct owner Program")]
    IncorrectOwnerProgram,
    #[msg("Account is not initialized")]
    UninitializedAccount,
    #[msg("Account is already initialized")]
    InitializedAccount,
    #[msg("Auth account is not valid")]
    InvalidAuthority,
    #[msg("Auth is not signer")]
    MissingRequiredSignature,
}

#[program]
pub mod token_treasury {
    use super::*;

    pub fn initialize_treasury(ctx: Context<InitializeTreasury>) -> Result<()> {
        ctx.accounts.treasury.bump = ctx.bumps.treasury;
        ctx.accounts.treasury.mint = *ctx.accounts.mint.to_account_info().key;
        ctx.accounts.treasury.authority = *ctx.accounts.authority.to_account_info().key;
        Ok(())
    }

    pub fn transfer_token(ctx: Context<TransferToken>, amount: u64) -> Result<()> {
        if !cmp_pubkeys(
            ctx.accounts.authority.to_account_info().key,
            &ctx.accounts.treasury.authority,
        ) {
            return Err(TreasuryError::InvalidAuthority.into());
        }

        if !cmp_pubkeys(ctx.accounts.treasury.to_account_info().owner, &id()) {
            return Err(TreasuryError::IncorrectOwnerProgram.into());
        }

        if !ctx.accounts.authority.is_signer {
            return err!(TreasuryError::MissingRequiredSignature);
        }

        transfer_checked(
            CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                TransferChecked {
                    from: ctx.accounts.treasury_ata.to_account_info(),
                    mint: ctx.accounts.mint.to_account_info(),
                    to: ctx.accounts.user_ata.to_account_info(),
                    authority: ctx.accounts.treasury.to_account_info(),
                },
                &[&[
                    b"treasury",
                    ctx.accounts.treasury.mint.as_ref(),
                    ctx.accounts.treasury.authority.as_ref(),
                    &[ctx.accounts.treasury.bump],
                ]],
            ),
            amount,
            ctx.accounts.mint.decimals,
        )?;

        Ok(())
    }
}

#[account]
#[derive(Default, InitSpace)]
pub struct Treasury {
    pub mint: Pubkey,
    pub authority: Pubkey,
    pub bump: u8,
}

#[derive(Accounts)]
pub struct InitializeTreasury<'info> {
    #[account(init, payer=payer, seeds=[b"treasury", mint.key().as_ref(), authority.key().as_ref()], bump, space=8+Treasury::INIT_SPACE)]
    pub treasury: Account<'info, Treasury>,
    #[account(
        init,
        payer=payer,
        associated_token::mint = mint,
        associated_token::authority = treasury,
        associated_token::token_program = token_program
      )]
    pub treasury_ata: Account<'info, TokenAccount>,
    pub mint: Account<'info, Mint>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub authority: Signer<'info>,
    pub rent: Sysvar<'info, Rent>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}

#[derive(Accounts)]
pub struct TransferToken<'info> {
    #[account(seeds=[b"treasury", treasury.mint.as_ref(), treasury.authority.as_ref()], bump=treasury.bump)]
    pub treasury: Account<'info, Treasury>,
    #[account(mut, associated_token::mint = treasury.mint, associated_token::authority = treasury)]
    pub treasury_ata: Account<'info, TokenAccount>,
    pub mint: Account<'info, Mint>,
    /// CHECK: USER Account
    pub user: UncheckedAccount<'info>,
    #[account(init_if_needed, payer=payer, associated_token::mint = mint, associated_token::authority = user)]
    pub user_ata: Account<'info, TokenAccount>,
    #[account(mut)]
    pub payer: Signer<'info>,
    pub authority: Signer<'info>,
    pub rent: Sysvar<'info, Rent>,
    pub system_program: Program<'info, System>,
    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
}
